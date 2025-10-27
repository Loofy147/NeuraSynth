import unittest
import os
import json

# Set the base directory to the project root
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in os.sys.path:
    os.sys.path.insert(0, basedir)

from src.app import create_app
from src.models import db, User, Project

class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.token = self.get_token()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_token(self):
        self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'password',
                'user_type': 'client'
            }),
            content_type='application/json'
        )
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'password'
            }),
            content_type='application/json'
        )
        return response.json['token']

    def test_create_project(self):
        response = self.client.post(
            '/api/v1/projects/create',
            headers={'Authorization': f'Bearer {self.token}'},
            data=json.dumps({
                'name': 'Test Project'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.query.count(), 1)
        self.assertEqual(Project.query.first().name, 'Test Project')

    def test_get_project(self):
        self.test_create_project()
        project = Project.query.first()
        response = self.client.get(
            f'/api/v1/projects/{project.id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['project']['name'], 'Test Project')

if __name__ == '__main__':
    unittest.main()
