import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import get_all_documents

print("Testing Program Progress Calculation...")
print("=" * 80)

# Get all data
programs = get_all_documents('programs')
all_types = get_all_documents('accreditation_types')
all_areas = get_all_documents('areas')
all_checklists = get_all_documents('checklists')
all_documents = get_all_documents('documents')

# Filter active programs
active_programs = [p for p in programs if p.get('is_active', False) and not p.get('is_archived', False)]
active_checklists = [c for c in all_checklists if c.get('is_active', False) and not c.get('is_archived', False)]
active_documents = [d for d in all_documents if d.get('is_active', False) and not d.get('is_archived', False)]

print(f"Active Programs: {len(active_programs)}")
print(f"Active Checklists: {len(active_checklists)}")
print(f"Active Documents: {len(active_documents)}")
print("\n" + "=" * 80)

for prog in active_programs[:5]:  # Test first 5 programs
    prog_id = prog.get('id')
    prog_name = prog.get('name', 'Unknown')
    
    print(f"\nProgram: {prog_name}")
    print("-" * 80)
    
    # Get types for this program
    prog_types = [t for t in all_types if t.get('program_id') == prog_id]
    print(f"  Types: {len(prog_types)}")
    
    if not prog_types:
        print(f"  Progress: 0%")
        continue
    
    type_progresses = []
    for prog_type in prog_types:
        type_id = prog_type.get('id')
        type_name = prog_type.get('name', 'Unknown Type')
        type_areas = [a for a in all_areas if (a.get('type_id') == type_id or a.get('accreditation_type_id') == type_id)]
        
        print(f"    Type: {type_name} - Areas: {len(type_areas)}")
        
        if not type_areas:
            type_progresses.append(0)
            continue
        
        area_progresses = []
        for area in type_areas:
            area_id = area.get('id')
            area_name = area.get('name', 'Unknown Area')
            area_checklists = [c for c in active_checklists if c.get('area_id') == area_id]
            
            if not area_checklists:
                area_progresses.append(0)
                continue
            
            total_checklists = len(area_checklists)
            completed_checklists = 0
            
            for checklist in area_checklists:
                checklist_id = checklist.get('id')
                checklist_docs = [d for d in active_documents if d.get('checklist_id') == checklist_id]
                has_approved = any(d.get('status') == 'approved' for d in checklist_docs)
                if has_approved:
                    completed_checklists += 1
            
            area_progress = (completed_checklists / total_checklists) * 100 if total_checklists > 0 else 0
            area_progresses.append(area_progress)
            print(f"      Area: {area_name} - {completed_checklists}/{total_checklists} checklists = {area_progress:.1f}%")
        
        type_progress = sum(area_progresses) / len(area_progresses) if area_progresses else 0
        type_progresses.append(type_progress)
        print(f"    Type Progress: {type_progress:.1f}%")
    
    prog_progress = round(sum(type_progresses) / len(type_progresses), 1) if type_progresses else 0
    print(f"  PROGRAM PROGRESS: {prog_progress}%")

print("\n" + "=" * 80)
print("Test complete!")
