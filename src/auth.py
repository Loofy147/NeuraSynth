from flask import Blueprint, request, jsonify, current_app
import jwt
import datetime
import bcrypt
import uuid
import json
from .models import db, User

auth = Blueprint('auth', __name__)

class AuthManager:
    """
    Enhanced Authentication Manager for NeuraSynth Studios
    """

    def __init__(self):
        """
        Initialize the authentication manager
        """
        self.salt_rounds = 12

    def register_user(self, email, password, user_type, profile_data=None):
        """
        Register a new user
        """
        try:
            if User.query.filter_by(email=email).first():
                return {
                    'success': False,
                    'message': 'User with this email already exists'
                }

            if '@' not in email or '.' not in email:
                return {
                    'success': False,
                    'message': 'Invalid email format'
                }

            if len(password) < 8:
                return {
                    'success': False,
                    'message': 'Password must be at least 8 characters long'
                }

            valid_user_types = ['freelancer', 'client', 'merchant', 'admin']
            if user_type not in valid_user_types:
                return {
                    'success': False,
                    'message': f'Invalid user type. Must be one of: {valid_user_types}'
                }

            user = User(email=email, password=password, user_type=user_type)
            db.session.add(user)
            db.session.commit()

            return {
                'success': True,
                'user_id': user.id,
                'message': 'User registered successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }

    def authenticate_user(self, email, password):
        """
        Authenticate user login
        """
        try:
            user = User.query.filter_by(email=email).first()

            if not user or not user.verify_password(password):
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }

            user_data = {
                'id': user.id,
                'email': user.email,
                'user_type': user.user_type
            }

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

auth_manager = AuthManager()

@auth.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint
    """
    try:
        data = request.get_json()

        required_fields = ['email', 'password', 'user_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        result = auth_manager.register_user(
            email=data['email'],
            password=data['password'],
            user_type=data['user_type'],
            profile_data=data.get('profile_data', {})
        )

        if result['success']:
            token = jwt.encode({
                'user_id': result['user_id'],
                'email': data['email'],
                'user_type': data['user_type'],
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                'success': True,
                'user_id': result['user_id'],
                'token': token,
                'message': 'User registered successfully'
            }), 201
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    """
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        result = auth_manager.authenticate_user(
            email=data['email'],
            password=data['password']
        )

        if result['success']:
            token = jwt.encode({
                'user_id': result['user']['id'],
                'email': result['user']['email'],
                'user_type': result['user']['user_type'],
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                'success': True,
                'token': token,
                'user': result['user']
            }), 200
        else:
            return jsonify({'error': result['message']}), 401

    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500
