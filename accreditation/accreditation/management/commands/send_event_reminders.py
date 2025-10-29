"""
Management command to send event reminder notifications
Run this daily via cron job or Task Scheduler:
python manage.py send_event_reminders
"""

from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from accreditation.firebase_utils import get_all_documents
from accreditation.notification_utils import notify_event_reminder, notify_event_today


class Command(BaseCommand):
    help = 'Send event reminder notifications for upcoming calendar events'

    def handle(self, *args, **options):
        try:
            # Get today's date
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            # Get all active calendar events
            all_events = get_all_documents('calendar_events')
            active_events = [
                event for event in all_events 
                if not event.get('is_archived', False) and event.get('status') == 'active'
            ]
            
            reminders_sent = 0
            today_notifications_sent = 0
            
            # Check each event
            for event in active_events:
                event_date_str = event.get('date')
                if not event_date_str:
                    continue
                
                try:
                    # Parse event date (format: YYYY-MM-DD)
                    event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
                    
                    # Check if event is tomorrow (1 day reminder)
                    if event_date == tomorrow:
                        notify_event_reminder(
                            event_id=event.get('id'),
                            event_title=event.get('title', 'Untitled Event'),
                            event_date=event_date_str,
                            event_description=event.get('description', '')
                        )
                        reminders_sent += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Reminder sent for: {event.get("title")} (tomorrow)')
                        )
                    
                    # Check if event is today
                    elif event_date == today:
                        notify_event_today(
                            event_id=event.get('id'),
                            event_title=event.get('title', 'Untitled Event'),
                            event_date=event_date_str,
                            event_description=event.get('description', '')
                        )
                        today_notifications_sent += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Today notification sent for: {event.get("title")}')
                        )
                        
                except ValueError:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Invalid date format for event: {event.get("title")}')
                    )
                    continue
            
            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                    f'Event Reminder Notifications Summary\n'
                    f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                    f'Tomorrow reminders sent: {reminders_sent}\n'
                    f'Today notifications sent: {today_notifications_sent}\n'
                    f'Total notifications: {reminders_sent + today_notifications_sent}\n'
                    f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error sending event reminders: {str(e)}')
            )
            import traceback
            traceback.print_exc()
