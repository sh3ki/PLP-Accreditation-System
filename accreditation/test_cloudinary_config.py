"""
Test if Cloudinary configuration is working
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accreditation.settings')
django.setup()

print("\n🔍 Checking Cloudinary Configuration:\n")
print("=" * 80)

# Check environment variables
api_key = os.environ.get('CLOUDINARY_API_KEY', '')
api_secret = os.environ.get('CLOUDINARY_API_SECRET', '')

print(f"API Key: {'✅ Set' if api_key else '❌ Not set'}")
print(f"API Secret: {'✅ Set' if api_secret else '❌ Not set'}")
print(f"Cloud Name: dygrh6ztt (hardcoded)")

if api_key and api_secret:
    print("\n✅ Credentials are available!")
    print("\nTesting Cloudinary connection...")
    
    try:
        import cloudinary
        import cloudinary.api
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name='dygrh6ztt',
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Test connection by pinging
        result = cloudinary.api.ping()
        print(f"✅ Cloudinary connection successful!")
        print(f"Response: {result}")
        
    except Exception as e:
        print(f"❌ Cloudinary connection failed: {str(e)}")
else:
    print("\n❌ Credentials not found in environment!")
    print("Please check your .env file")

print("\n" + "=" * 80)
