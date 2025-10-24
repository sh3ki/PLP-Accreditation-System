"""
Script to rename areas from "Area A", "Area B" to "Area 1", "Area 2" in Firebase

Usage: python rename_areas_to_numbers.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.firebase_utils import firestore_helper

def rename_areas():
    """Rename areas from letters to numbers"""
    
    print("🔄 Starting area renaming process...")
    print()
    
    # Mapping from letter to number
    area_mapping = {
        'Area A': 'Area 1',
        'Area B': 'Area 2',
        'Area C': 'Area 3',
        'Area D': 'Area 4',
        'Area E': 'Area 5',
        'Area F': 'Area 6',
        'Area G': 'Area 7',
        'Area H': 'Area 8',
        'Area I': 'Area 9',
        'Area J': 'Area 10'
    }
    
    try:
        # Get all areas
        areas_collection = firestore_helper.db.collection('areas')
        areas = areas_collection.stream()
        
        updated_count = 0
        skipped_count = 0
        
        for area_doc in areas:
            area_data = area_doc.to_dict()
            current_name = area_data.get('name', '')
            
            # Check if this area needs to be renamed
            if current_name in area_mapping:
                new_name = area_mapping[current_name]
                
                # Update the area
                areas_collection.document(area_doc.id).update({
                    'name': new_name
                })
                
                print(f"   ✓ Renamed: {current_name} → {new_name} (ID: {area_doc.id})")
                updated_count += 1
            else:
                skipped_count += 1
        
        print()
        print("=" * 80)
        print(f"✅ Area renaming completed!")
        print("=" * 80)
        print(f"   • Areas updated: {updated_count}")
        print(f"   • Areas skipped: {skipped_count}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    rename_areas()
