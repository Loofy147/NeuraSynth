import unittest
import os

# Set the base directory to the project root
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in os.sys.path:
    os.sys.path.insert(0, basedir)

from src.app import create_app
from src.models import db, User

class AppTestCase(unittest.TestCase):
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

    def test_health_check(self):
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'healthy')

if __name__ == '__main__':
    unittest.main()
