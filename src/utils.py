from .auth import AuthManager
from .user import UserManager
from .project import ProjectManager
from .matching import MatchingEngine
from .contributors_hub import ContributorsHub
from .advanced_ai_systems import AdvancedMatchingEngine
from flask import request, jsonify
import jwt
from functools import wraps
from flask import current_app

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
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated
