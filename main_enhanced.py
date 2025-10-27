# -*- coding: utf-8 -*-
"""
NeuraSynth Studios - Enhanced Main Application
Orchestrator-AI Production Unit - Backend Core System

This is the main Flask application that serves as the backend for NeuraSynth Studios.
It integrates all the core modules including authentication, user management, 
project management, AI matching, and contributors hub.

⚠️ SUSPICIOUS POINT: Database connection needs to be properly configured
⚠️ SUSPICIOUS POINT: JWT secret key should be environment variable
⚠️ SUSPICIOUS POINT: CORS origins should be configurable
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
import datetime
import uuid
import json
from functools import wraps

# Internal imports - Core modules
from auth import AuthManager
from user import UserManager
from project import ProjectManager
from matching import MatchingEngine
from contributors_hub import ContributorsHub
from advanced_ai_systems import AdvancedMatchingEngine

# Initialize Flask app
app = Flask(__name__)

# ⚠️ SUSPICIOUS POINT: This should be an environment variable
app.config['SECRET_KEY'] = 'neurasynth-super-secret-key-2024'

# Enable CORS for all routes
# ⚠️ SUSPICIOUS POINT: In production, specify exact origins
CORS(app, origins=['*'])

# Initialize core managers
auth_manager = AuthManager()
user_manager = UserManager()
project_manager = ProjectManager()
matching_engine = MatchingEngine()
contributors_hub = ContributorsHub()
ai_matching_engine = AdvancedMatchingEngine()

# JWT token verification decorator
def token_required(f):
    """
    Decorator to verify JWT tokens for protected routes
    
    ⚠️ SUSPICIOUS POINT: Token expiration handling needs improvement
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode JWT token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# Health check endpoint
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API is running
    
    # ESSENTIAL STEP: Always verify this endpoint works first
    """
    return jsonify({
        'status': 'healthy',
        'service': 'NeuraSynth Studios API',
        'version': '2.0.0',
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

# Authentication endpoints
@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """
    User registration endpoint
    
    # ESSENTIAL STEP: Validate all input data
    ⚠️ SUSPICIOUS POINT: Need better input validation
    """
    try:
        data = request.get_json()
        
        # Basic validation
        required_fields = ['email', 'password', 'user_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Register user using auth manager
        result = auth_manager.register_user(
            email=data['email'],
            password=data['password'],
            user_type=data['user_type'],
            profile_data=data.get('profile_data', {})
        )
        
        if result['success']:
            # Generate JWT token
            token = jwt.encode({
                'user_id': result['user_id'],
                'email': data['email'],
                'user_type': data['user_type'],
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'success': True,
                'user_id': result['user_id'],
                'token': token,
                'message': 'User registered successfully'
            }), 201
        else:
            return jsonify({'error': result['message']}), 400
            
    except Exception as e:
        # ⚠️ SUSPICIOUS POINT: Better error logging needed
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    # ESSENTIAL STEP: Verify credentials securely
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate user
        result = auth_manager.authenticate_user(
            email=data['email'],
            password=data['password']
        )
        
        if result['success']:
            # Generate JWT token
            token = jwt.encode({
                'user_id': result['user']['id'],
                'email': result['user']['email'],
                'user_type': result['user']['user_type'],
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'success': True,
                'token': token,
                'user': result['user']
            }), 200
        else:
            return jsonify({'error': result['message']}), 401
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

# User management endpoints
@app.route('/api/v1/users/<user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    """
    Get user profile information
    
    # ESSENTIAL STEP: Check user permissions
    ⚠️ SUSPICIOUS POINT: Privacy controls needed
    """
    try:
        # Check if user can access this profile
        if current_user_id != user_id:
            # ⚠️ SUSPICIOUS POINT: Implement proper permission checking
            pass
        
        user_data = user_manager.get_user_profile(user_id)
        
        if user_data:
            return jsonify({
                'success': True,
                'user': user_data
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500

@app.route('/api/v1/users/<user_id>/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user_id, user_id):
    """
    Update user profile
    
    # ESSENTIAL STEP: Validate user ownership
    """
    try:
        # Check if user can update this profile
        if current_user_id != user_id:
            return jsonify({'error': 'Unauthorized to update this profile'}), 403
        
        data = request.get_json()
        
        result = user_manager.update_user_profile(user_id, data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            }), 200
        else:
            return jsonify({'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

# Project management endpoints
@app.route('/api/v1/projects/create', methods=['POST'])
@token_required
def create_project(current_user_id):
    """
    Create a new project
    
    # ESSENTIAL STEP: Validate project data and trigger AI matching
    """
    try:
        data = request.get_json()
        
        # Add client_id to project data
        data['client_id'] = current_user_id
        
        # Create project
        result = project_manager.create_project(data)
        
        if result['success']:
            project_id = result['project_id']
            
            # Trigger AI matching for the new project
            # ⚠️ SUSPICIOUS POINT: This might be slow, consider async processing
            try:
                matches = ai_matching_engine.find_matches_for_project(project_id)
                
                return jsonify({
                    'success': True,
                    'project_id': project_id,
                    'ai_matches': matches[:5],  # Return top 5 matches
                    'message': 'Project created successfully'
                }), 201
                
            except Exception as matching_error:
                # Project created but matching failed
                return jsonify({
                    'success': True,
                    'project_id': project_id,
                    'ai_matches': [],
                    'message': 'Project created but AI matching failed',
                    'matching_error': str(matching_error)
                }), 201
        else:
            return jsonify({'error': result['message']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to create project: {str(e)}'}), 500

@app.route('/api/v1/projects/<project_id>', methods=['GET'])
@token_required
def get_project(current_user_id, project_id):
    """
    Get project details
    
    # ESSENTIAL STEP: Check project access permissions
    """
    try:
        project_data = project_manager.get_project(project_id)
        
        if project_data:
            # ⚠️ SUSPICIOUS POINT: Implement proper access control
            return jsonify({
                'success': True,
                'project': project_data
            }), 200
        else:
            return jsonify({'error': 'Project not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to get project: {str(e)}'}), 500

# AI Matching endpoints
@app.route('/api/v1/matching/find-matches/<project_id>', methods=['GET'])
@token_required
def find_matches(current_user_id, project_id):
    """
    Find AI-powered matches for a project
    
    # ESSENTIAL STEP: Verify project ownership or access
    """
    try:
        # ⚠️ SUSPICIOUS POINT: Check if user has access to this project
        
        start_time = datetime.datetime.utcnow()
        
        # Get matches using AI engine
        matches = ai_matching_engine.find_matches_for_project(project_id)
        
        end_time = datetime.datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return jsonify({
            'success': True,
            'matches': matches,
            'total_matches': len(matches),
            'processing_time_ms': round(processing_time, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to find matches: {str(e)}'}), 500

# Contributors Hub endpoints
@app.route('/api/v1/contributors/equity/<contributor_id>', methods=['GET'])
@token_required
def get_contributor_equity(current_user_id, contributor_id):
    """
    Get contributor equity information
    
    # ESSENTIAL STEP: Verify contributor access rights
    ⚠️ SUSPICIOUS POINT: Sensitive financial data - need strict access control
    """
    try:
        # Check if user can access this equity information
        if current_user_id != contributor_id:
            # ⚠️ SUSPICIOUS POINT: Implement role-based access control
            pass
        
        equity_data = contributors_hub.get_equity_holdings(contributor_id)
        
        return jsonify({
            'success': True,
            'equity': equity_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get equity data: {str(e)}'}), 500

@app.route('/api/v1/contributors/performance/<contributor_id>', methods=['GET'])
@token_required
def get_contributor_performance(current_user_id, contributor_id):
    """
    Get contributor performance metrics
    
    # ESSENTIAL STEP: Verify access permissions
    """
    try:
        performance_data = contributors_hub.get_performance_metrics(contributor_id)
        
        return jsonify({
            'success': True,
            'performance': performance_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get performance data: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    """
    Main application entry point
    
    # ESSENTIAL STEP: Configure for production deployment
    ⚠️ SUSPICIOUS POINT: Debug mode should be False in production
    """
    print("🚀 Starting NeuraSynth Studios Backend...")
    print("📊 Orchestrator-AI Production Unit: Backend Core System")
    print("🔗 API Documentation: http://localhost:5001/api/v1/health")
    
    # ⚠️ SUSPICIOUS POINT: Use environment variables for configuration
    app.run(
        host='0.0.0.0',  # Allow external access
        port=5001,
        debug=True  # ⚠️ SUSPICIOUS POINT: Set to False in production
    )

