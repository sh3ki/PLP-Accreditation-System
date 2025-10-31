"""
Context processors for adding global template variables
"""
import os
import time
from typing import Dict
from .firebase_utils import get_all_documents

_APPEARANCE_CACHE: Dict[str, object] = {
    'data': None,
    'ts': 0,
}


def _default_appearance():
    return {
        'theme_color': '#4a9d4f',
        'system_title': 'PLP Accreditation System',
        'logo_url': '',
    }


def appearance_settings(request):
    """
    Add appearance settings to all template contexts.
    IMPORTANT: Avoid blocking page render on Firestore when quota is exhausted.
    - Skip Firestore fetch on auth pages (login etc.) and when disabled via env.
    - Use a small in-memory cache to reduce repeated calls.
    - Fall back to defaults immediately on any error.
    """
    # Fast path: allow disabling via env var
    if os.getenv('DISABLE_APPEARANCE_FETCH', '').lower() in ('1', 'true', 'yes'):  # pragma: no cover
        return _default_appearance()

    # Skip Firestore call on authentication routes to prevent 500s if quota is hit
    try:
        path = getattr(request, 'path', '') or ''
        if path.startswith('/auth/'):
            return _default_appearance()
    except Exception:
        # If anything odd with request, use defaults
        return _default_appearance()

    # Serve from cache if fresh (5 minutes TTL)
    now = time.time()
    cached = _APPEARANCE_CACHE.get('data')
    ts = _APPEARANCE_CACHE.get('ts', 0)
    if cached and (now - ts) < 300:
        return cached  # type: ignore[return-value]

    # Attempt to fetch from Firestore, but fail fast and use defaults on any error
    try:
        settings_docs = get_all_documents('system_settings')
        appearance_doc = next((d for d in settings_docs if d.get('setting_type') == 'appearance'), None)
        if appearance_doc:
            result = {
                'theme_color': appearance_doc.get('theme_color', '#4a9d4f'),
                'system_title': appearance_doc.get('system_title', 'PLP Accreditation System'),
                'logo_url': appearance_doc.get('logo_url', ''),
            }
            _APPEARANCE_CACHE['data'] = result
            _APPEARANCE_CACHE['ts'] = now
            return result
    except Exception as e:
        # Do not block; log and fall back to cached or defaults
        try:
            print(f"Error loading appearance settings in context processor: {e}")
        except Exception:
            pass

    # Return cached if available, else defaults
    if cached:
        return cached  # type: ignore[return-value]
    return _default_appearance()
