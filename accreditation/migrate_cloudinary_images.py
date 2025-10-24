"""
Script to migrate images from old Cloudinary account to new account
using Cloudinary's fetch/upload feature to maintain folder structure and filenames
"""

import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure new Cloudinary account
cloudinary.config(
    cloud_name='dygrh6ztt',
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# List of all images to migrate from old account
IMAGES_TO_MIGRATE = [
    {
        'old_url': 'https://res.cloudinary.com/dlu2bqrda/image/upload/v1759219218/PLP_LOGO_ujtdgd.png',
        'public_id': 'PLP_LOGO_ujtdgd',
        'folder': None,  # Root folder
        'description': 'PLP Logo - Used in dashboards'
    },
    {
        'old_url': 'https://res.cloudinary.com/dlu2bqrda/image/upload/v1760105137/default-profile-account-unknown-icon-black-silhouette-free-vector_jdlpve.jpg',
        'public_id': 'default-profile-account-unknown-icon-black-silhouette-free-vector_jdlpve',
        'folder': None,  # Root folder
        'description': 'Default Profile Picture - Used in user management'
    },
    {
        'old_url': 'https://res.cloudinary.com/dlu2bqrda/image/upload/v1760107585/compsci_tcgeee.png',
        'public_id': 'compsci_tcgeee',
        'folder': None,  # Root folder
        'description': 'CCS Logo - Used in department'
    },
    {
        'old_url': 'https://res.cloudinary.com/dlu2bqrda/image/upload/v1759218759/bg_qhybsq.jpg',
        'public_id': 'bg_qhybsq',
        'folder': None,  # Root folder
        'description': 'Login Background Image'
    },
    # Add more images here if needed
]

def migrate_image(image_info):
    """
    Fetch image from old Cloudinary account and upload to new account
    """
    try:
        print(f"\n{'='*60}")
        print(f"Migrating: {image_info['description']}")
        print(f"Source URL: {image_info['old_url']}")
        
        # Build the public_id with folder if specified
        if image_info['folder']:
            public_id = f"{image_info['folder']}/{image_info['public_id']}"
        else:
            public_id = image_info['public_id']
        
        # Upload from URL (fetch from old account)
        upload_result = cloudinary.uploader.upload(
            image_info['old_url'],
            public_id=public_id,
            overwrite=True,
            resource_type='image',
            type='upload'
        )
        
        new_url = upload_result.get('secure_url', '')
        print(f"✅ SUCCESS!")
        print(f"New URL: {new_url}")
        print(f"Public ID: {upload_result.get('public_id', 'N/A')}")
        print(f"Format: {upload_result.get('format', 'N/A')}")
        print(f"Size: {upload_result.get('bytes', 0)} bytes")
        
        return {
            'success': True,
            'old_url': image_info['old_url'],
            'new_url': new_url,
            'public_id': upload_result.get('public_id'),
            'description': image_info['description']
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {
            'success': False,
            'old_url': image_info['old_url'],
            'error': str(e),
            'description': image_info['description']
        }

def main():
    """
    Main migration function
    """
    print("="*60)
    print("CLOUDINARY IMAGE MIGRATION TOOL")
    print("="*60)
    print(f"Target Account: dygrh6ztt")
    print(f"Total Images to Migrate: {len(IMAGES_TO_MIGRATE)}")
    print("="*60)
    
    print("\nStarting image migration...")
    
    # Migrate all images
    results = []
    for image_info in IMAGES_TO_MIGRATE:
        result = migrate_image(image_info)
        results.append(result)
    
    # Print summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print("\n📋 URL MAPPING (for updating your code):")
        print("-"*60)
        for result in successful:
            print(f"\n{result['description']}:")
            print(f"  Old: {result['old_url']}")
            print(f"  New: {result['new_url']}")
    
    if failed:
        print("\n⚠️  FAILED MIGRATIONS:")
        print("-"*60)
        for result in failed:
            print(f"\n{result['description']}:")
            print(f"  URL: {result['old_url']}")
            print(f"  Error: {result['error']}")
    
    print("\n" + "="*60)
    print("Migration completed!")
    print("="*60)
    
    # Save results to file for reference
    with open('cloudinary_migration_results.txt', 'w') as f:
        f.write("CLOUDINARY MIGRATION RESULTS\n")
        f.write("="*60 + "\n\n")
        f.write(f"Migration Date: {__import__('datetime').datetime.now()}\n")
        f.write(f"Total Images: {len(results)}\n")
        f.write(f"Successful: {len(successful)}\n")
        f.write(f"Failed: {len(failed)}\n\n")
        
        f.write("URL MAPPINGS:\n")
        f.write("-"*60 + "\n")
        for result in results:
            if result['success']:
                f.write(f"\n{result['description']}:\n")
                f.write(f"  Old: {result['old_url']}\n")
                f.write(f"  New: {result['new_url']}\n")
                f.write(f"  Public ID: {result['public_id']}\n")
    
    print(f"\n📄 Results saved to: cloudinary_migration_results.txt")

if __name__ == '__main__':
    # Check if credentials are set
    if not os.environ.get('CLOUDINARY_API_KEY') or not os.environ.get('CLOUDINARY_API_SECRET'):
        print("❌ ERROR: Cloudinary credentials not found in environment variables!")
        print("Please make sure .env file is present with CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET")
        exit(1)
    
    main()
