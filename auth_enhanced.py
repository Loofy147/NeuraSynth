# -*- coding: utf-8 -*-
"""
NeuraSynth Studios - Enhanced Authentication Manager
Orchestrator-AI Production Unit - Authentication System

This module handles user authentication, registration, and JWT token management
for the NeuraSynth Studios platform.

⚠️ SUSPICIOUS POINT: Password hashing salt rounds should be configurable
⚠️ SUSPICIOUS POINT: Rate limiting for login attempts needed
"""

import bcrypt
import uuid
import datetime
import json

class AuthManager:
    """
    Enhanced Authentication Manager for NeuraSynth Studios
    
    Handles user registration, login, password hashing, and session management.
    """
    
    def __init__(self):
        """
        Initialize the authentication manager
        
        # ESSENTIAL STEP: Set up secure password hashing parameters
        """
        self.salt_rounds = 12  # ⚠️ SUSPICIOUS POINT: Should be environment variable
        
        # In-memory storage for demo (replace with database in production)
        # ⚠️ SUSPICIOUS POINT: This should be replaced with proper database
        self.users_db = {}
        self.profiles_db = {}
        
        # Initialize with some demo users for testing
        self._initialize_demo_users()
    
    def _initialize_demo_users(self):
        """
        Initialize demo users for testing purposes
        
        # ESSENTIAL STEP: Remove this in production
        ⚠️ SUSPICIOUS POINT: Demo data should not exist in production
        """
        demo_users = [
            {
                'email': 'freelancer@neurasynth.com',
                'password': 'password123',
                'user_type': 'freelancer',
                'profile_data': {
                    'name': 'John Doe',
                    'skills': ['Python', 'React', 'AI'],
                    'experience_years': 5
                }
            },
            {
                'email': 'client@neurasynth.com',
                'password': 'password123',
                'user_type': 'client',
                'profile_data': {
                    'name': 'Jane Smith',
                    'company': 'Tech Corp',
                    'industry': 'Technology'
                }
            }
        ]
        
        for user_data in demo_users:
            self.register_user(
                email=user_data['email'],
                password=user_data['password'],
                user_type=user_data['user_type'],
                profile_data=user_data['profile_data']
            )
    
    def _hash_password(self, password):
        """
        Hash password using bcrypt
        
        # ESSENTIAL STEP: Ensure secure password hashing
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password, hashed_password):
        """
        Verify password against hash
        
        # ESSENTIAL STEP: Secure password verification
        """
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def register_user(self, email, password, user_type, profile_data=None):
        """
        Register a new user
        
        Args:
            email (str): User email address
            password (str): Plain text password
            user_type (str): Type of user (freelancer, client, merchant, etc.)
            profile_data (dict): Additional profile information
        
        Returns:
            dict: Registration result with success status and user_id
        
        # ESSENTIAL STEP: Validate all input data thoroughly
        ⚠️ SUSPICIOUS POINT: Need comprehensive input validation
        """
        try:
            # Check if user already exists
            if email in self.users_db:
                return {
                    'success': False,
                    'message': 'User with this email already exists'
                }
            
            # Validate email format (basic validation)
            if '@' not in email or '.' not in email:
                return {
                    'success': False,
                    'message': 'Invalid email format'
                }
            
            # Validate password strength
            if len(password) < 8:
                return {
                    'success': False,
                    'message': 'Password must be at least 8 characters long'
                }
            
            # Validate user type
            valid_user_types = ['freelancer', 'client', 'merchant', 'admin']
            if user_type not in valid_user_types:
                return {
                    'success': False,
                    'message': f'Invalid user type. Must be one of: {valid_user_types}'
                }
            
            # Generate unique user ID
            user_id = str(uuid.uuid4())
            
            # Hash password
            hashed_password = self._hash_password(password)
            
            # Create user record
            user_record = {
                'id': user_id,
                'email': email,
                'password_hash': hashed_password,
                'user_type': user_type,
                'created_at': datetime.datetime.utcnow().isoformat(),
                'updated_at': datetime.datetime.utcnow().isoformat(),
                'is_active': True,
                'email_verified': False  # ⚠️ SUSPICIOUS POINT: Implement email verification
            }
            
            # Store user
            self.users_db[email] = user_record
            
            # Create profile if profile_data provided
            if profile_data:
                profile_record = {
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'created_at': datetime.datetime.utcnow().isoformat(),
                    'updated_at': datetime.datetime.utcnow().isoformat(),
                    **profile_data
                }
                self.profiles_db[user_id] = profile_record
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User registered successfully'
            }
            
        except Exception as e:
            # ⚠️ SUSPICIOUS POINT: Better error logging needed
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }
    
    def authenticate_user(self, email, password):
        """
        Authenticate user login
        
        Args:
            email (str): User email
            password (str): Plain text password
        
        Returns:
            dict: Authentication result with user data if successful
        
        # ESSENTIAL STEP: Implement rate limiting for failed attempts
        ⚠️ SUSPICIOUS POINT: No rate limiting implemented
        """
        try:
            # Check if user exists
            if email not in self.users_db:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            user_record = self.users_db[email]
            
            # Check if account is active
            if not user_record.get('is_active', True):
                return {
                    'success': False,
                    'message': 'Account is deactivated'
                }
            
            # Verify password
            if not self._verify_password(password, user_record['password_hash']):
                # ⚠️ SUSPICIOUS POINT: Log failed login attempts
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            # Update last login time
            user_record['last_login'] = datetime.datetime.utcnow().isoformat()
            
            # Prepare user data for response (exclude sensitive information)
            user_data = {
                'id': user_record['id'],
                'email': user_record['email'],
                'user_type': user_record['user_type'],
                'created_at': user_record['created_at'],
                'email_verified': user_record['email_verified']
            }
            
            # Include profile data if available
            if user_record['id'] in self.profiles_db:
                user_data['profile'] = self.profiles_db[user_record['id']]
            
            return {
                'success': True,
                'user': user_data,
                'message': 'Authentication successful'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Authentication failed: {str(e)}'
            }
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id (str): User ID
        
        Returns:
            dict: User data or None if not found
        
        # ESSENTIAL STEP: Ensure data privacy
        """
        try:
            # Find user by ID
            for email, user_record in self.users_db.items():
                if user_record['id'] == user_id:
                    # Return user data without sensitive information
                    user_data = {
                        'id': user_record['id'],
                        'email': user_record['email'],
                        'user_type': user_record['user_type'],
                        'created_at': user_record['created_at'],
                        'email_verified': user_record['email_verified']
                    }
                    
                    # Include profile data if available
                    if user_id in self.profiles_db:
                        user_data['profile'] = self.profiles_db[user_id]
                    
                    return user_data
            
            return None
            
        except Exception as e:
            # ⚠️ SUSPICIOUS POINT: Better error handling needed
            return None
    
    def update_user_password(self, user_id, old_password, new_password):
        """
        Update user password
        
        Args:
            user_id (str): User ID
            old_password (str): Current password
            new_password (str): New password
        
        Returns:
            dict: Update result
        
        # ESSENTIAL STEP: Verify old password before updating
        """
        try:
            # Find user
            user_record = None
            user_email = None
            
            for email, record in self.users_db.items():
                if record['id'] == user_id:
                    user_record = record
                    user_email = email
                    break
            
            if not user_record:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            # Verify old password
            if not self._verify_password(old_password, user_record['password_hash']):
                return {
                    'success': False,
                    'message': 'Current password is incorrect'
                }
            
            # Validate new password
            if len(new_password) < 8:
                return {
                    'success': False,
                    'message': 'New password must be at least 8 characters long'
                }
            
            # Hash new password
            new_hashed_password = self._hash_password(new_password)
            
            # Update password
            user_record['password_hash'] = new_hashed_password
            user_record['updated_at'] = datetime.datetime.utcnow().isoformat()
            
            return {
                'success': True,
                'message': 'Password updated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Password update failed: {str(e)}'
            }
    
    def deactivate_user(self, user_id):
        """
        Deactivate user account
        
        Args:
            user_id (str): User ID
        
        Returns:
            dict: Deactivation result
        
        # ESSENTIAL STEP: Implement proper account deactivation
        ⚠️ SUSPICIOUS POINT: Consider data retention policies
        """
        try:
            # Find and deactivate user
            for email, user_record in self.users_db.items():
                if user_record['id'] == user_id:
                    user_record['is_active'] = False
                    user_record['deactivated_at'] = datetime.datetime.utcnow().isoformat()
                    user_record['updated_at'] = datetime.datetime.utcnow().isoformat()
                    
                    return {
                        'success': True,
                        'message': 'User account deactivated successfully'
                    }
            
            return {
                'success': False,
                'message': 'User not found'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Deactivation failed: {str(e)}'
            }

