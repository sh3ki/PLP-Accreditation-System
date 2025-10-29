"""
Notification Utility Functions
Handles creation and management of user notifications
"""

from datetime import datetime
from accreditation.firebase_utils import create_document, get_all_documents, update_document
import uuid


def create_notification(user_id, notification_type, title, message, details=None, data=None):
    """
    Create a notification for a user
    
    Args:
        user_id: ID of the user to notify
        notification_type: Type of notification (document_upload, document_approved, etc.)
        title: Notification title
        message: Notification message
        details: Optional details string
        data: Optional dictionary with additional data
    
    Returns:
        notification_id: ID of created notification
    """
    try:
        print(f"[CREATE NOTIFICATION] Creating notification for user: {user_id}")
        print(f"[CREATE NOTIFICATION] Type: {notification_type}, Title: {title}")
        
        notification_data = {
            'user_id': user_id,
            'type': notification_type,
            'title': title,
            'message': message,
            'details': details or '',
            'data': data or {},
            'is_read': False,
            'created_at': datetime.now().isoformat(),
        }
        
        notification_id = str(uuid.uuid4())
        create_document('notifications', notification_data, notification_id)
        
        print(f"[CREATE NOTIFICATION] SUCCESS! Notification ID: {notification_id}")
        return notification_id
    except Exception as e:
        import traceback
        print(f"[CREATE NOTIFICATION ERROR] Failed: {str(e)}")
        print(f"[CREATE NOTIFICATION ERROR] Traceback: {traceback.format_exc()}")
        return None


def notify_document_upload(document_id, document_name, department_name, program_name, 
                          type_name, area_name, checklist_name, uploader_email, uploader_name):
    """
    Create notifications for document upload
    Notifies QA staff about new uploads
    """
    try:
        print(f"[NOTIFY UPLOAD] Starting notification for document: {document_name}")
        
        # Get all QA staff (qa_head and qa_admin)
        from accreditation.firebase_utils import get_all_documents
        all_users = get_all_documents('users')
        
        print(f"[NOTIFY UPLOAD] Total users found: {len(all_users)}")
        
        qa_staff = [user for user in all_users if user.get('role') in ['qa_head', 'qa_admin']]
        
        print(f"[NOTIFY UPLOAD] QA staff found: {len(qa_staff)}")
        for qa_user in qa_staff:
            print(f"[NOTIFY UPLOAD] QA User: {qa_user.get('email')} - Role: {qa_user.get('role')}")
        
        title = f"New Document Uploaded"
        message = f"{uploader_name} uploaded '{document_name}'"
        details = f"{department_name} > {program_name} > {type_name} > {area_name} > {checklist_name}"
        
        data = {
            'document_id': document_id,
            'document_name': document_name,
            'department': department_name,
            'program': program_name,
            'type': type_name,
            'area': area_name,
            'checklist': checklist_name,
            'uploader': uploader_email
        }
        
        # Notify all QA staff
        for qa_user in qa_staff:
            print(f"[NOTIFY UPLOAD] Creating notification for: {qa_user.get('email')}")
            create_notification(
                user_id=qa_user.get('id'),
                notification_type='document_upload',
                title=title,
                message=message,
                details=details,
                data=data
            )
            
        print(f"[NOTIFY UPLOAD] All notifications created successfully!")
    except Exception as e:
        import traceback
        print(f"[NOTIFY UPLOAD ERROR] Failed: {str(e)}")
        print(f"[NOTIFY UPLOAD ERROR] Traceback: {traceback.format_exc()}")


def notify_document_status_change(document_id, document_name, status, uploader_id, 
                                  department_name, program_name, type_name, area_name, 
                                  checklist_name, reviewer_name, comment=None):
    """
    Create notification for document approval/disapproval
    Notifies the uploader about status change
    """
    try:
        if status == 'approved':
            title = "Document Approved ✓"
            message = f"Your document '{document_name}' has been approved by {reviewer_name}"
            notification_type = 'document_approved'
        else:  # disapproved
            title = "Document Needs Revision ✗"
            message = f"Your document '{document_name}' was disapproved by {reviewer_name}"
            if comment:
                message += f"\n\nReason: {comment}"
            notification_type = 'document_disapproved'
        
        details = f"{department_name} > {program_name} > {type_name} > {area_name} > {checklist_name}"
        
        data = {
            'document_id': document_id,
            'document_name': document_name,
            'status': status,
            'department': department_name,
            'program': program_name,
            'type': type_name,
            'area': area_name,
            'checklist': checklist_name,
            'reviewer': reviewer_name,
            'comment': comment or ''
        }
        
        # Notify the uploader
        create_notification(
            user_id=uploader_id,
            notification_type=notification_type,
            title=title,
            message=message,
            details=details,
            data=data
        )
        
    except Exception as e:
        print(f"Error notifying document status change: {str(e)}")


def notify_event_created(event_id, event_title, event_date, event_description, created_by):
    """
    Create notifications for new calendar event
    Notifies all users about new event
    """
    try:
        # Get all active users
        all_users = get_all_documents('users')
        active_users = [user for user in all_users if user.get('is_active', True)]
        
        title = "New Event Added 📅"
        message = f"{event_title} on {event_date}"
        details = event_description[:100] + '...' if len(event_description) > 100 else event_description
        
        data = {
            'event_id': event_id,
            'event_title': event_title,
            'event_date': event_date,
            'created_by': created_by
        }
        
        # Notify all active users
        for user in active_users:
            create_notification(
                user_id=user.get('id'),
                notification_type='event_created',
                title=title,
                message=message,
                details=details,
                data=data
            )
            
    except Exception as e:
        print(f"Error notifying event created: {str(e)}")


def notify_event_reminder(event_id, event_title, event_date, event_description):
    """
    Create event reminder notifications (1 day before)
    Called by scheduled task
    """
    try:
        # Get all active users
        all_users = get_all_documents('users')
        active_users = [user for user in all_users if user.get('is_active', True)]
        
        title = "Event Reminder ⏰"
        message = f"Tomorrow: {event_title}"
        details = f"Don't forget! {event_description[:100]}"
        
        data = {
            'event_id': event_id,
            'event_title': event_title,
            'event_date': event_date,
            'reminder_type': '1_day_before'
        }
        
        # Notify all active users
        for user in active_users:
            create_notification(
                user_id=user.get('id'),
                notification_type='event_reminder',
                title=title,
                message=message,
                details=details,
                data=data
            )
            
    except Exception as e:
        print(f"Error notifying event reminder: {str(e)}")


def notify_event_today(event_id, event_title, event_date, event_description):
    """
    Create event day notifications
    Called by scheduled task
    """
    try:
        # Get all active users
        all_users = get_all_documents('users')
        active_users = [user for user in all_users if user.get('is_active', True)]
        
        title = "Event Today! 🎯"
        message = f"Today: {event_title}"
        details = event_description[:100] if event_description else ''
        
        data = {
            'event_id': event_id,
            'event_title': event_title,
            'event_date': event_date,
            'reminder_type': 'event_day'
        }
        
        # Notify all active users
        for user in active_users:
            create_notification(
                user_id=user.get('id'),
                notification_type='event_today',
                title=title,
                message=message,
                details=details,
                data=data
            )
            
    except Exception as e:
        print(f"Error notifying event today: {str(e)}")


def get_user_notifications(user_id, limit=10):
    """
    Get notifications for a specific user
    
    Args:
        user_id: ID of the user
        limit: Maximum number of notifications to return (default: 10 most recent)
    
    Returns:
        List of notifications sorted by creation date (newest first)
    """
    try:
        all_notifications = get_all_documents('notifications')
        user_notifications = [
            notif for notif in all_notifications 
            if notif.get('user_id') == user_id
        ]
        
        # Sort by creation date (newest first)
        user_notifications.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Limit to 10 most recent
        return user_notifications[:limit]
        
    except Exception as e:
        print(f"Error getting user notifications: {str(e)}")
        return []


def get_unread_count(user_id):
    """
    Get count of unread notifications for a user
    
    Args:
        user_id: ID of the user
    
    Returns:
        Count of unread notifications
    """
    try:
        all_notifications = get_all_documents('notifications')
        unread_notifications = [
            notif for notif in all_notifications 
            if notif.get('user_id') == user_id and not notif.get('is_read', False)
        ]
        
        return len(unread_notifications)
        
    except Exception as e:
        print(f"Error getting unread count: {str(e)}")
        return 0


def mark_notification_as_read(notification_id):
    """
    Mark a notification as read
    
    Args:
        notification_id: ID of the notification
    
    Returns:
        True if successful, False otherwise
    """
    try:
        update_document('notifications', notification_id, {'is_read': True})
        return True
    except Exception as e:
        print(f"Error marking notification as read: {str(e)}")
        return False


def mark_all_as_read(user_id):
    """
    Mark all notifications as read for a user
    
    Args:
        user_id: ID of the user
    
    Returns:
        Number of notifications marked as read
    """
    try:
        all_notifications = get_all_documents('notifications')
        user_unread = [
            notif for notif in all_notifications 
            if notif.get('user_id') == user_id and not notif.get('is_read', False)
        ]
        
        count = 0
        for notif in user_unread:
            if mark_notification_as_read(notif.get('id')):
                count += 1
        
        return count
        
    except Exception as e:
        print(f"Error marking all as read: {str(e)}")
        return 0
