"""
Cloudinary utility functions for file uploads
"""
import os
import re

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
        
        # Get credentials from environment variables
        api_key = os.environ.get('CLOUDINARY_API_KEY', '')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET', '')
        
        # Check if credentials are available
        if not api_key or not api_secret:
            raise ValueError(
                "Cloudinary credentials not found. "
                "Please set CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in your .env file. "
                "Copy .env.example to .env and add your credentials."
            )
        
        # Configure Cloudinary with your credentials
        cloudinary.config(
            cloud_name='dygrh6ztt',
            api_key=api_key,
            api_secret=api_secret,
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


def delete_image_from_cloudinary(image_url):
    """
    Delete an image from Cloudinary using its URL
    
    Args:
        image_url: Full Cloudinary URL of the image
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Get credentials from environment variables
        api_key = os.environ.get('CLOUDINARY_API_KEY', '')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET', '')
        
        # Check if credentials are available
        if not api_key or not api_secret:
            print("Cloudinary credentials not found. Skipping deletion.")
            return False
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name='dygrh6ztt',
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/dygrh6ztt/image/upload/v1234567890/folder/filename.ext
        public_id = extract_public_id_from_url(image_url)
        
        if not public_id:
            print(f"Could not extract public_id from URL: {image_url}")
            return False
        
        # Delete the image
        result = cloudinary.uploader.destroy(public_id, resource_type='image')
        
        if result.get('result') == 'ok':
            print(f"Successfully deleted image: {public_id}")
            return True
        else:
            print(f"Failed to delete image: {public_id}. Result: {result}")
            return False
        
    except ImportError:
        print("Warning: cloudinary package not installed.")
        return False
    except Exception as e:
        print(f"Error deleting from Cloudinary: {str(e)}")
        return False


def extract_public_id_from_url(url):
    """
    Extract the public_id from a Cloudinary URL
    
    Args:
        url: Full Cloudinary URL
        
    Returns:
        str: Public ID with folder path (e.g., "departments/abc123")
    """
    try:
        # Pattern: https://res.cloudinary.com/{cloud_name}/image/upload/v{version}/{public_id}.{ext}
        # We need to extract everything after /upload/v{version}/ and remove the extension
        
        if not url or 'cloudinary.com' not in url:
            return None
        
        # Find the position after '/upload/'
        upload_index = url.find('/upload/')
        if upload_index == -1:
            return None
        
        # Get everything after '/upload/'
        after_upload = url[upload_index + 8:]  # 8 is len('/upload/')
        
        # Remove version prefix (v1234567890/)
        parts = after_upload.split('/')
        if len(parts) > 1 and parts[0].startswith('v') and parts[0][1:].isdigit():
            # Remove version part
            parts = parts[1:]
        
        # Reconstruct path without extension
        path = '/'.join(parts)
        
        # Remove file extension
        if '.' in path:
            path = path.rsplit('.', 1)[0]
        
        return path
        
    except Exception as e:
        print(f"Error extracting public_id: {str(e)}")
        return None


def upload_document_to_cloudinary(file, folder='documents'):
    """
    Upload a document file (doc, docx, pdf, ppt, etc.) to Cloudinary
    
    Args:
        file: Django UploadedFile object
        folder: Cloudinary folder name
        
    Returns:
        str: Cloudinary URL of uploaded document
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Get credentials from environment variables
        api_key = os.environ.get('CLOUDINARY_API_KEY', '')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET', '')
        
        # Check if credentials are available
        if not api_key or not api_secret:
            raise ValueError(
                "Cloudinary credentials not found. "
                "Please set CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in your .env file."
            )
        
        # Configure Cloudinary with your credentials
        cloudinary.config(
            cloud_name='dygrh6ztt',
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Determine resource type based on file extension
        file_name = file.name if hasattr(file, 'name') else str(file)
        file_ext = file_name.split('.')[-1].lower()
        
        # Map file types to Cloudinary resource types
        if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
            resource_type = 'image'
        elif file_ext in ['mp4', 'avi', 'mov', 'wmv']:
            resource_type = 'video'
        else:
            # For documents (doc, docx, pdf, ppt, xls, etc.)
            resource_type = 'raw'
        
        # Upload the file with public access
        upload_options = {
            'folder': folder,
            'resource_type': resource_type,
            'access_mode': 'public',  # Ensure public access
        }
        
        # For PDFs, enable page transformations for preview capabilities
        if file_ext == 'pdf':
            upload_options['pages'] = True  # Enable multi-page PDFs
            upload_options['flags'] = 'attachment'  # Force download when accessed
        
        upload_result = cloudinary.uploader.upload(file, **upload_options)
        
        return upload_result.get('secure_url', '')
        
    except ImportError:
        # Cloudinary not installed, return empty string
        print("Warning: cloudinary package not installed. Please install it: pip install cloudinary")
        return ''
    except Exception as e:
        print(f"Error uploading document to Cloudinary: {str(e)}")
        raise e


def delete_document_from_cloudinary(document_url):
    """
    Delete a document from Cloudinary using its URL
    
    Args:
        document_url: Full Cloudinary URL of the document
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Get credentials from environment variables
        api_key = os.environ.get('CLOUDINARY_API_KEY', '')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET', '')
        
        # Check if credentials are available
        if not api_key or not api_secret:
            print("Cloudinary credentials not found. Skipping deletion.")
            return False
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name='dygrh6ztt',
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Extract public_id from URL
        public_id = extract_public_id_from_url(document_url)
        
        if not public_id:
            print(f"Could not extract public_id from URL: {document_url}")
            return False
        
        # Determine resource type from URL
        if '/image/' in document_url:
            resource_type = 'image'
        elif '/video/' in document_url:
            resource_type = 'video'
        else:
            resource_type = 'raw'
        
        # Delete the document
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        
        if result.get('result') == 'ok':
            print(f"Successfully deleted document: {public_id}")
            return True
        else:
            print(f"Failed to delete document: {public_id}. Result: {result}")
            return False
        
    except ImportError:
        print("Warning: cloudinary package not installed.")
        return False
    except Exception as e:
        print(f"Error deleting document from Cloudinary: {str(e)}")
        return False


def upload_file_to_cloudinary(file_data, filename, folder='uploads'):
    """
    Upload any file (PDF, Excel, etc.) to Cloudinary
    
    Args:
        file_data: File bytes data
        filename: Name of the file
        folder: Cloudinary folder name
        
    Returns:
        str: Cloudinary URL of uploaded file
    """
    try:
        import cloudinary
        import cloudinary.uploader
        import io
        
        # Get credentials from environment variables
        api_key = os.environ.get('CLOUDINARY_API_KEY', '')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET', '')
        
        # Check if credentials are available
        if not api_key or not api_secret:
            raise ValueError(
                "Cloudinary credentials not found. "
                "Please set CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in your .env file."
            )
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name='dygrh6ztt',
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Convert bytes to file-like object if needed
        if isinstance(file_data, bytes):
            file_data = io.BytesIO(file_data)
        
        # Upload the file
        upload_result = cloudinary.uploader.upload(
            file_data,
            folder=folder,
            resource_type='raw',  # Use 'raw' for non-image files like PDF, Excel
            public_id=filename.rsplit('.', 1)[0],  # Remove extension for public_id
            format=filename.rsplit('.', 1)[-1] if '.' in filename else None,  # Keep original extension
            overwrite=True
        )
        
        return upload_result.get('secure_url', '')
        
    except ImportError:
        print("Warning: cloudinary package not installed. Please install it: pip install cloudinary")
        raise
    except Exception as e:
        print(f"Error uploading file to Cloudinary: {str(e)}")
        raise e
