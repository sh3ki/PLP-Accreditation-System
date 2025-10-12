"""
Cloudinary utility functions for file uploads
"""
import os

def upload_image_to_cloudinary(file, folder='uploads'):
    """
    Upload an image file to Cloudinary
    
    Args:
        file: Django UploadedFile object
        folder: Cloudinary folder name
        
    Returns:
        str: Cloudinary URL of uploaded image
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Configure Cloudinary with your credentials
        cloudinary.config(
            cloud_name='dlu2bqrda',
            api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET', ''),
            secure=True
        )
        
        # Upload the file
        upload_result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type='image',
            transformation=[
                {'width': 500, 'height': 500, 'crop': 'limit'},
                {'quality': 'auto:good'}
            ]
        )
        
        return upload_result.get('secure_url', '')
        
    except ImportError:
        # Cloudinary not installed, return empty string
        print("Warning: cloudinary package not installed. Please install it: pip install cloudinary")
        return ''
    except Exception as e:
        print(f"Error uploading to Cloudinary: {str(e)}")
        raise e
