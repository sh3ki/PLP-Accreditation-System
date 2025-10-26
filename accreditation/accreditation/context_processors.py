"""
Context processors for adding global template variables
"""
from .firebase_utils import get_all_documents

def appearance_settings(request):
    """
    Add appearance settings to all template contexts
    This prevents flickering by loading theme color before page render
    """
    try:
        # Get all system settings documents
        settings_docs = get_all_documents('system_settings')
        
        # Find the appearance settings document
        appearance_doc = None
        for doc in settings_docs:
            if doc.get('setting_type') == 'appearance':
                appearance_doc = doc
                break
        
        if appearance_doc:
            return {
                'theme_color': appearance_doc.get('theme_color', '#4a9d4f'),
                'system_title': appearance_doc.get('system_title', 'PLP Accreditation System'),
                'logo_url': appearance_doc.get('logo_url', ''),
            }
    except Exception as e:
        print(f"Error loading appearance settings in context processor: {e}")
    
    # Return defaults if error occurs
    return {
        'theme_color': '#4a9d4f',
        'system_title': 'PLP Accreditation System',
        'logo_url': '',
    }
