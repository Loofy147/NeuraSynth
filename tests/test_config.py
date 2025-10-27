import unittest
import os

# Set the base directory to the project root
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in os.sys.path:
    os.sys.path.insert(0, basedir)

from src.app import create_app
from src.config import config

class TestConfig(unittest.TestCase):
    def test_development_config(self):
        app = create_app('development')
        self.assertTrue(app.config['DEBUG'])
        self.assertEqual(
            app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///' + os.path.join(basedir, 'database', 'dev.sqlite')
        )

    def test_testing_config(self):
        app = create_app('testing')
        self.assertTrue(app.config['TESTING'])
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite://')

    def test_production_config(self):
        app = create_app('production')
        self.assertFalse(app.config.get('DEBUG', False))
        self.assertEqual(
            app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///' + os.path.join(basedir, 'database', 'data.sqlite')
        )

if __name__ == '__main__':
    unittest.main()
