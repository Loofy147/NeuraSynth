# -*- coding: utf-8 -*-
"""
Tests for the financial endpoints.
"""

import unittest
import json
from src.app import create_app
from src.models import db, Expense, Invoice, Payment, User
from src.auth import auth_manager
from datetime import datetime, date

class FinancialTestCase(unittest.TestCase):
    """This class represents the financial test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.user = User(username='testuser', email='test@example.com', password='password')
        self.expense = {
            "title": "Test Expense",
            "amount": 100.00,
            "expense_date": date.today().isoformat(),
            "organization_id": "org1"
        }
        self.invoice = {
            "invoice_number": "INV-001",
            "title": "Test Invoice",
            "subtotal": 500.00,
            "client_name": "Test Client",
            "issue_date": date.today().isoformat(),
            "due_date": date.today().isoformat(),
            "organization_id": "org1"
        }
        self.payment = {
            "payment_reference": "PAY-001",
            "amount": 500.00,
            "payment_method": "credit_card",
            "organization_id": "org1"
        }

        # binds the app to the current context
        with self.app.app_context():
            db.create_all()
            auth_manager.register_user(email='test@example.com', password='password', user_type='client')
            self.user_id = User.query.filter_by(email='test@example.com').first().id

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _get_token(self):
        """Helper method to get a token."""
        res = self.client().post('/api/v1/auth/login', data=json.dumps({
            "email": "test@example.com",
            "password": "password"
        }), content_type='application/json')
        return json.loads(res.data.decode())['token']

    def test_create_expense(self):
        """Test API can create an expense."""
        token = self._get_token()
        res = self.client().post('/api/v1/financial/expenses',
                                 headers={'Authorization': f'Bearer {token}'},
                                 data=json.dumps(self.expense),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('Test Expense', str(res.data))

    def test_create_invoice(self):
        """Test API can create an invoice."""
        token = self._get_token()
        res = self.client().post('/api/v1/financial/invoices',
                                 headers={'Authorization': f'Bearer {token}'},
                                 data=json.dumps(self.invoice),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('Test Invoice', str(res.data))

    def test_create_payment(self):
        """Test API can create a payment."""
        token = self._get_token()
        res = self.client().post('/api/v1/financial/payments',
                                 headers={'Authorization': f'Bearer {token}'},
                                 data=json.dumps(self.payment),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('PAY-001', str(res.data))

if __name__ == "__main__":
    unittest.main()
