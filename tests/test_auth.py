import unittest
import os
import json

# Set the base directory to the project root
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in os.sys.path:
    os.sys.path.insert(0, basedir)

from src.app import create_app
from src.models import db, User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register(self):
        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'password',
                'user_type': 'freelancer'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().email, 'test@example.com')

    def test_login(self):
        self.test_register()
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'password'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

if __name__ == '__main__':
    unittest.main()
