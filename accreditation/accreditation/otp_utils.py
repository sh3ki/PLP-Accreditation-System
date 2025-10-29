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


def send_otp_email(user_email, user_name, otp):
    """Send OTP via email"""
    subject = 'OTP Verification - PLP Accreditation System'
    
    message = f"""
Hello {user_name},

Your One-Time Password (OTP) for logging into the PLP Accreditation System is:

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
            <h1>🔐 OTP Verification</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px;">PLP Accreditation System</p>
        </div>
        <div class="content">
            <p>Hello <strong>{user_name}</strong>,</p>
            <p>Your One-Time Password (OTP) for logging into the PLP Accreditation System is:</p>
            
            <div class="otp-box">
                <div class="otp-code">{otp}</div>
                <div class="info-text">Valid for {settings.OTP_EXPIRY_MINUTES} minutes</div>
            </div>
            
            <p>Please enter this code on the verification page to continue.</p>
            
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


def store_otp(user_uid, otp):
    """Store OTP in Firestore with expiry time"""
    from accreditation.settings import db
    
    if not db:
        return False
    
    try:
        expiry_time = datetime.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        
        otp_data = {
            'otp': otp,
            'created_at': firestore.SERVER_TIMESTAMP,
            'expires_at': expiry_time,
            'verified': False,
            'attempts': 0
        }
        
        db.collection('otp_verifications').document(user_uid).set(otp_data)
        return True
    except Exception as e:
        print(f"Error storing OTP: {e}")
        return False


def verify_otp(user_uid, entered_otp):
    """Verify OTP and check expiry"""
    from accreditation.settings import db
    
    if not db:
        return {'success': False, 'message': 'Database connection error'}
    
    try:
        otp_ref = db.collection('otp_verifications').document(user_uid)
        otp_doc = otp_ref.get()
        
        if not otp_doc.exists:
            return {'success': False, 'message': 'No OTP found. Please request a new one.'}
        
        otp_data = otp_doc.to_dict()
        
        # Check if already verified
        if otp_data.get('verified', False):
            return {'success': False, 'message': 'OTP already used. Please request a new one.'}
        
        # Check expiry
        expires_at = otp_data.get('expires_at')
        if expires_at and datetime.now() > expires_at:
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
        print(f"Error verifying OTP: {e}")
        return {'success': False, 'message': 'Verification error. Please try again.'}


def delete_otp(user_uid):
    """Delete OTP after successful verification"""
    from accreditation.settings import db
    
    if not db:
        return False
    
    try:
        db.collection('otp_verifications').document(user_uid).delete()
        return True
    except Exception as e:
        print(f"Error deleting OTP: {e}")
        return False


def resend_otp(user_uid, user_email, user_name):
    """Resend a new OTP"""
    # Generate new OTP
    new_otp = generate_otp(settings.OTP_LENGTH)
    
    # Send email
    if send_otp_email(user_email, user_name, new_otp):
        # Store in database
        if store_otp(user_uid, new_otp):
            return {'success': True, 'message': 'New OTP sent successfully'}
        else:
            return {'success': False, 'message': 'Failed to store OTP'}
    else:
        return {'success': False, 'message': 'Failed to send email'}
