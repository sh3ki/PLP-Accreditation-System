from django.core.management.base import BaseCommand
from accreditation.firebase_utils import get_all_documents, update_document


class Command(BaseCommand):
    help = 'Update College of Computer Studies logo URL'

    def handle(self, *args, **options):
        logo_url = "https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284240/compsci_tcgeee.png"
        
        # Get all departments
        departments = get_all_documents('departments')
        
        # Find College of Computer Studies
        ccs_dept = None
        for dept in departments:
            if 'Computer' in dept.get('name', '') or 'CCS' in dept.get('code', ''):
                ccs_dept = dept
                break
        
        if ccs_dept:
            dept_id = ccs_dept.get('code')
            dept_name = ccs_dept.get('name')
            
            # Update the logo URL
            update_document('departments', dept_id, {'logo_url': logo_url})
            
            self.stdout.write(self.style.SUCCESS(
                f'✅ Successfully updated logo for "{dept_name}" (ID: {dept_id})'
            ))
            self.stdout.write(f'Logo URL: {logo_url}')
        else:
            self.stdout.write(self.style.WARNING(
                '⚠️  College of Computer Studies department not found'
            ))
            self.stdout.write('Available departments:')
            for dept in departments:
                self.stdout.write(f'  - {dept.get("name")} ({dept.get("code")})')
