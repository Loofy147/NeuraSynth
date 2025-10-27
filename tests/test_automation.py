# -*- coding: utf-8 -*-
"""
Tests for the automation endpoints.
"""

import unittest
import json
from src.app import create_app
from src.models import db, AutomationRule

class AutomationTestCase(unittest.TestCase):
    """This class represents the automation test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.rule = {
            "id": "test_rule_1",
            "name": "Test Rule",
            "trigger_type": "event_based",
            "conditions": {"event_type": "project_created"},
            "actions": [{"type": "send_notification", "recipient_id": "admin"}]
        }

        # binds the app to the current context
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_automation_rule(self):
        """Test API can create an automation rule."""
        res = self.client().post('/api/v1/automation/rules', data=json.dumps(self.rule), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('Automation rule added successfully', str(res.data))

    def test_get_automation_stats(self):
        """Test API can get automation stats."""
        res = self.client().get('/api/v1/automation/stats')
        self.assertEqual(res.status_code, 200)
        self.assertIn('total_rules', str(res.data))

    def test_remove_automation_rule(self):
        """Test API can delete an automation rule."""
        # First, add a rule
        with self.app.app_context():
            rule = AutomationRule(**self.rule)
            db.session.add(rule)
            db.session.commit()
            rule_id = rule.id

        res = self.client().delete(f'/api/v1/automation/rules/{rule_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Automation rule removed successfully', str(res.data))

if __name__ == "__main__":
    unittest.main()
