"""
Custom User Model for Firebase Firestore

This area defines the User model and authentication system using Firebase Firestore
as the backend database instead of traditional Django models.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from accreditation.firebase_utils import firestore_helper
from datetime import datetime
import hashlib
import secrets
from typing import Optional, Dict, Any


class UserRole:
    """User role constants"""
    QA_HEAD = 'qa_head'
    QA_ADMIN = 'qa_admin'
    DEPARTMENT_USER = 'department_user'
    
    CHOICES = [
        (QA_HEAD, 'QA Head'),
        (QA_ADMIN, 'QA Admin'),
        (DEPARTMENT_USER, 'Department User'),
    ]
    
    @classmethod
    def get_role_display(cls, role):
        """Get display name for role"""
        role_dict = dict(cls.CHOICES)
        return role_dict.get(role, role)


class FirebaseUser:
    """
    Custom User class that works with Firebase Firestore
    """
    
    def __init__(self, email=None, user_data=None):
        if user_data:
            # Initialize from Firestore data
            self.id = user_data.get('id')
            self.email = user_data.get('email')
            self.first_name = user_data.get('first_name', '')
            self.last_name = user_data.get('last_name', '')
            self.role = user_data.get('role', UserRole.DEPARTMENT_USER)
            self.is_active = user_data.get('is_active', True)
            self.is_password_changed = user_data.get('is_password_changed', False)
            self.date_joined = user_data.get('date_joined')
            self.last_login = user_data.get('last_login')
            self.password_hash = user_data.get('password_hash')
        else:
            # Initialize empty user
            self.id = None
            self.email = email
            self.first_name = ''
            self.last_name = ''
            self.role = UserRole.DEPARTMENT_USER
            self.is_active = True
            self.is_password_changed = False
            self.date_joined = None
            self.last_login = None
            self.password_hash = None
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def role_display(self):
        """Get role display name"""
        return UserRole.get_role_display(self.role)
    
    @property
    def is_qa_head(self):
        """Check if user is QA Head"""
        return self.role == UserRole.QA_HEAD
    
    @property  
    def is_qa_admin(self):
        """Check if user is QA Admin"""
        return self.role == UserRole.QA_ADMIN
    
    @property
    def is_department_user(self):
        """Check if user is Department User"""
        return self.role == UserRole.DEPARTMENT_USER
    
    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False for authenticated users"""
        return False
    
    def set_password(self, raw_password):
        """Set password hash"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          raw_password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        self.password_hash = f"{salt}${password_hash.hex()}"
    
    def check_password(self, raw_password):
        """Check if password is correct"""
        if not self.password_hash:
            return False
        
        try:
            salt, stored_hash = self.password_hash.split('$')
            password_hash = hashlib.pbkdf2_hmac('sha256',
                                              raw_password.encode('utf-8'),
                                              salt.encode('utf-8'),
                                              100000)
            return stored_hash == password_hash.hex()
        except (ValueError, AttributeError):
            return False
    
    def save(self):
        """Save user to Firestore"""
        user_data = {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'password_hash': self.password_hash,
            'last_login': self.last_login,
        }
        
        if self.id:
            # Update existing user
            firestore_helper.update_document('users', self.id, user_data)
        else:
            # Create new user
            user_data['date_joined'] = datetime.now()
            self.id = firestore_helper.create_document('users', user_data)
            self.date_joined = user_data['date_joined']
        
        return self
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now()
        if self.id:
            firestore_helper.update_document('users', self.id, {
                'last_login': self.last_login
            })
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        try:
            users = firestore_helper.query_documents('users', 'email', '==', email, limit=1)
            if users:
                return cls(user_data=users[0])
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        try:
            user_data = firestore_helper.get_document('users', user_id)
            if user_data:
                return cls(user_data=user_data)
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @classmethod
    def create_user(cls, email, password, first_name='', last_name='', role=UserRole.DEPARTMENT_USER):
        """Create a new user"""
        # Check if user already exists
        if cls.get_by_email(email):
            raise ValueError(f"User with email {email} already exists")
        
        user = cls(email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.role = role
        user.set_password(password)
        user.save()
        
        return user
    
    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user with email and password"""
        user = cls.get_by_email(email)
        if user and user.is_active and user.check_password(password):
            user.update_last_login()
            return user
        return None
    
    @classmethod
    def get_all_users(cls, role=None):
        """Get all users, optionally filtered by role"""
        try:
            if role:
                users_data = firestore_helper.query_documents('users', 'role', '==', role)
            else:
                users_data = firestore_helper.get_all_documents('users')
            
            return [cls(user_data=user_data) for user_data in users_data]
        except Exception as e:
            print(f"Error getting users: {e}")
            return []


class AnonymousUser:
    """Anonymous user class"""
    
    def __init__(self):
        self.id = None
        self.email = None
        self.is_authenticated = False
        self.is_anonymous = True
        self.is_active = False
        self.role = None
    
    @property
    def is_qa_head(self):
        return False
    
    @property
    def is_qa_admin(self):
        return False
    
    @property
    def is_department_user(self):
        return False


# Authentication Backend
class FirebaseAuthBackend:
    """
    Custom authentication backend for Firebase
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        """Authenticate user"""
        if email and password:
            return FirebaseUser.authenticate(email, password)
        return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return FirebaseUser.get_by_id(user_id)
        except Exception:
            return None


# Utility functions for creating default users
def create_default_users():
    """Create default users for testing"""
    try:
        # Create QA Head
        if not FirebaseUser.get_by_email('qahead@plpasig.edu.ph'):
            FirebaseUser.create_user(
                email='qahead@plpasig.edu.ph',
                password='qahead123',
                first_name='QA',
                last_name='Head',
                middle_name='',
                role=UserRole.QA_HEAD,
                department='CCS'
            )
            print("Created QA Head user: qahead@plpasig.edu.ph")
        
        # Create QA Admin
        if not FirebaseUser.get_by_email('qaadmin@plpasig.edu.ph'):
            FirebaseUser.create_user(
                email='qaadmin@plpasig.edu.ph',
                password='qaadmin123',
                first_name='QA',
                last_name='Admin',
                middle_name='',
                role=UserRole.QA_ADMIN,
                department='CCS'
            )
            print("Created QA Admin user: qaadmin@plpasig.edu.ph")
        
        # Create Department User (CCS)
        if not FirebaseUser.get_by_email('ccsuser@plpasig.edu.ph'):
            FirebaseUser.create_user(
                email='ccsuser@plpasig.edu.ph',
                password='ccsuser123',
                first_name='CCS',
                last_name='User',
                middle_name='',
                role=UserRole.DEPARTMENT_USER,
                department='CCS'
            )
            print("Created Department User (CCS): ccsuser@plpasig.edu.ph")
        
        # Create Department User (CED)
        if not FirebaseUser.get_by_email('ceduser@plpasig.edu.ph'):
            FirebaseUser.create_user(
                email='ceduser@plpasig.edu.ph',
                password='ceduser123',
                first_name='CED',
                last_name='User',
                middle_name='',
                role=UserRole.DEPARTMENT_USER,
                department='CED'
            )
            print("Created Department User (CED): ceduser@plpasig.edu.ph")
        
        # Create Department User (CAS)
        if not FirebaseUser.get_by_email('casuser@plpasig.edu.ph'):
            FirebaseUser.create_user(
                email='casuser@plpasig.edu.ph',
                password='casuser123',
                first_name='CAS',
                last_name='User',
                middle_name='',
                role=UserRole.DEPARTMENT_USER,
                department='CAS'
            )
            print("Created Department User (CAS): casuser@plpasig.edu.ph")
            
    except Exception as e:
        print(f"Error creating default users: {e}")