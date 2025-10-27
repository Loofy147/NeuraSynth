from flask import request, jsonify
from . import users
from ..user import UserManager
from ..utils import token_required

user_manager = UserManager()

@users.route('/<user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    """
    Get user profile information
    """
    try:
        # Check if user can access this profile
        if current_user_id != user_id:
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

@users.route('/<user_id>/profile', methods=['PUT'])
@token_required
def update_user_profile(current_user_id, user_id):
    """
    Update user profile
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
