from datetime import datetime
from typing import Optional, Dict, Any
from accreditation.firebase_utils import create_document


def _now_iso():
    return datetime.utcnow().isoformat() + 'Z'


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    Handles proxies and load balancers correctly.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def log_audit(user: Optional[Dict[str, Any]], action_type: str, resource_type: str, resource_id: Optional[str] = None, details: Optional[str] = None, status: str = 'success', ip: Optional[str] = None) -> None:
    """
    Write an audit record to Firestore collection 'audit_trail'.

    user: a dict with at least 'id' and 'email' or None
    action_type: 'login', 'logout', 'document_upload', 'report_generation', 'report_download', 'create', 'update', 'delete'
    resource_type: e.g. 'user', 'document', 'report', 'department', 'session'
    resource_id: optional id of the resource acted upon
    details: human-readable description of the action (e.g., "Updated profile of John Doe")
    status: 'success' or 'failed'
    ip: optional client IP address
    """
    try:
        user_id = None
        user_email = None
        user_name = None
        if isinstance(user, dict):
            user_id = user.get('id') or user.get('uid')
            user_email = user.get('email')
            user_name = user.get('name') or user.get('displayName') or f"{user.get('first_name','')} {user.get('last_name','')}".strip()

        audit = {
            'timestamp': _now_iso(),
            'user_id': user_id,
            'user_email': user_email,
            'user_name': user_name,
            'action_type': action_type,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or '',
            'status': status,
            'ip': ip,
        }

        # Use create_document helper to persist
        create_document('audit_trail', audit)
    except Exception as e:
        # Swallow exceptions to avoid impacting main flow; log to console for debugging
        try:
            print(f"Error writing audit log: {e}")
        except Exception:
            pass
