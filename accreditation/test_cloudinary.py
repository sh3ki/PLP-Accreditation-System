"""
Test Cloudinary upload and delete functions
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

from accreditation.cloudinary_utils import extract_public_id_from_url

# Test URLs
test_urls = [
    'https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284239/PLP_LOGO_ujtdgd.png',
    'https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284240/departments/compsci_tcgeee.png',
    'https://res.cloudinary.com/dygrh6ztt/image/upload/v1761284240/default-profile-account-unknown-icon-black-silhouette-free-vector_jdlpve.jpg',
]

print("\n🧪 Testing Public ID Extraction:\n")
print("=" * 80)

for url in test_urls:
    public_id = extract_public_id_from_url(url)
    print(f"\nURL: {url}")
    print(f"Public ID: {public_id}")
    print("-" * 80)

print("\n✅ Test complete!")
