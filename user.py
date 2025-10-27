# -*- coding: utf-8 -*-
"""
NeuraSynth Studios - User Manager
Simple user management for testing
"""

class UserManager:
    def __init__(self):
        self.users = {}
    
    def get_user_profile(self, user_id):
        return self.users.get(user_id, None)
    
    def update_user_profile(self, user_id, data):
        if user_id in self.users:
            self.users[user_id].update(data)
            return {'success': True}
        return {'success': False, 'message': 'User not found'}

