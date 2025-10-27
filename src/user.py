from .models import User, db

class UserManager:
    def get_user_profile(self, user_id):
        user = User.query.get(user_id)
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
            }
        return None

    def update_user_profile(self, user_id, data):
        user = User.query.get(user_id)
        if user:
            for key, value in data.items():
                if hasattr(user, key) and key != 'id':
                    setattr(user, key, value)
            db.session.commit()
            return {'success': True}
        return {'success': False, 'message': 'User not found'}
