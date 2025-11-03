"""
OTP Utility Functions for Email Verification
Handles OTP generation, storage, validation, and email sending
"""

import random
import string
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from google.cloud import firestore


def generate_otp(length=6):
    """Generate a random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(user_email, user_name, otp, purpose='login'):
    """Send OTP via email
    
    Args:
        user_email: User's email address
        user_name: User's full name
        otp: The OTP code
        purpose: Either 'login' or 'password_reset'
    """
    if purpose == 'password_reset':
        subject = 'Password Reset OTP - PLP Accreditation System'
        title = '🔑 Password Reset'
        intro = 'Your One-Time Password (OTP) for resetting your password is:'
        instruction = 'Please enter this code on the password reset page to continue.'
    else:
        subject = 'OTP Verification - PLP Accreditation System'
        title = '🔐 OTP Verification'
        intro = 'Your One-Time Password (OTP) for logging into the PLP Accreditation System is:'
        instruction = 'Please enter this code on the verification page to continue.'
    
    message = f"""
Hello {user_name},

{intro}

{otp}

This OTP is valid for {settings.OTP_EXPIRY_MINUTES} minutes.

If you did not request this OTP, please ignore this email.

Best regards,
PLP Accreditation System
    """
    
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: #4a9d4f;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .otp-box {{
            background: #f8f9fa;
            border: 2px dashed #4a9d4f;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 30px 0;
        }}
        .otp-code {{
            font-size: 36px;
            font-weight: bold;
            color: #4a9d4f;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }}
        .info-text {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
            font-size: 14px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px;">PLP Accreditation System</p>
        </div>
        <div class="content">
            <p>Hello <strong>{user_name}</strong>,</p>
            <p>{intro}</p>
            
            <div class="otp-box">
                <div class="otp-code">{otp}</div>
                <div class="info-text">Valid for {settings.OTP_EXPIRY_MINUTES} minutes</div>
            </div>
            
            <p>{instruction}</p>
            
            <div class="warning">
                <strong>⚠️ Security Notice:</strong> If you did not request this OTP, please ignore this email and contact your administrator immediately.
            </div>
        </div>
        <div class="footer">
            <p>This is an automated message from PLP Accreditation System.</p>
            <p>Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False


def store_otp(user_uid, otp, purpose='login'):
    """Store OTP in Firestore with expiry time
    
    Args:
        user_uid: User's unique ID
        otp: The OTP code
        purpose: Either 'login' or 'password_reset'
    """
    from accreditation.settings import db
    
    if not db:
        return False
    
    try:
        expiry_time = datetime.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        
        otp_data = {
            'otp': otp,
            'purpose': purpose,
            'created_at': firestore.SERVER_TIMESTAMP,
            'expires_at': expiry_time,
            'verified': False,
            'attempts': 0
        }
        
        # Use different collection based on purpose
        collection_name = f'otp_{purpose}' if purpose == 'password_reset' else 'otp_verifications'
        db.collection(collection_name).document(user_uid).set(otp_data)
        return True
    except Exception as e:
        print(f"Error storing OTP: {e}")
        return False


def verify_otp(user_uid, entered_otp, purpose='login'):
    """Verify OTP and check expiry
    
    Args:
        user_uid: User's unique ID
        entered_otp: The OTP entered by user
        purpose: Either 'login' or 'password_reset'
    """
    from accreditation.settings import db
    
    if not db:
        return {'success': False, 'message': 'Database connection error'}
    
    try:
        # Use different collection based on purpose
        collection_name = f'otp_{purpose}' if purpose == 'password_reset' else 'otp_verifications'
        otp_ref = db.collection(collection_name).document(user_uid)
        otp_doc = otp_ref.get()
        
        if not otp_doc.exists:
            return {'success': False, 'message': 'No OTP found. Please request a new one.'}
        
        otp_data = otp_doc.to_dict()
        
        # Check if already verified
        if otp_data.get('verified', False):
            return {'success': False, 'message': 'OTP already used. Please request a new one.'}
        
        # Check expiry - handle both datetime and Firestore timestamp
        expires_at = otp_data.get('expires_at')
        if expires_at:
            # Convert Firestore timestamp to datetime if needed
            if hasattr(expires_at, 'timestamp'):
                # It's a Firestore timestamp, convert to datetime
                from datetime import timezone
                expires_at = datetime.fromtimestamp(expires_at.timestamp(), tz=timezone.utc)
                current_time = datetime.now(timezone.utc)
            else:
                # It's already a datetime object
                current_time = datetime.now()
            
            if current_time > expires_at:
                return {'success': False, 'message': 'OTP has expired. Please request a new one.'}
        
        # Check attempts (max 5 attempts)
        attempts = otp_data.get('attempts', 0)
        if attempts >= 5:
            return {'success': False, 'message': 'Too many failed attempts. Please request a new OTP.'}
        
        # Verify OTP
        stored_otp = otp_data.get('otp')
        if stored_otp == entered_otp:
            # Mark as verified
            otp_ref.update({'verified': True})
            return {'success': True, 'message': 'OTP verified successfully'}
        else:
            # Increment attempts
            otp_ref.update({'attempts': attempts + 1})
            remaining = 5 - (attempts + 1)
            return {
                'success': False, 
                'message': f'Invalid OTP. {remaining} attempts remaining.'
            }
    
    except Exception as e:
        import traceback
        print(f"Error verifying OTP: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return {'success': False, 'message': 'Verification error. Please try again.'}


def delete_otp(user_uid, purpose='login'):
    """Delete OTP after successful verification
    
    Args:
        user_uid: User's unique ID
        purpose: Either 'login' or 'password_reset'
    """
    from accreditation.settings import db
    
    if not db:
        return False
    
    try:
        collection_name = f'otp_{purpose}' if purpose == 'password_reset' else 'otp_verifications'
        db.collection(collection_name).document(user_uid).delete()
        return True
    except Exception as e:
        print(f"Error deleting OTP: {e}")
        return False


def resend_otp(user_uid, user_email, user_name, purpose='login'):
    """Resend a new OTP
    
    Args:
        user_uid: User's unique ID
        user_email: User's email address
        user_name: User's full name
        purpose: Either 'login' or 'password_reset'
    """
    # Generate new OTP
    new_otp = generate_otp(settings.OTP_LENGTH)
    
    # Send email
    if send_otp_email(user_email, user_name, new_otp, purpose=purpose):
        # Store in database
        if store_otp(user_uid, new_otp, purpose=purpose):
            return {'success': True, 'message': 'New OTP sent successfully'}
        else:
            return {'success': False, 'message': 'Failed to store OTP'}
    else:
        return {'success': False, 'message': 'Failed to send email'}
