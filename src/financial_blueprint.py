# -*- coding: utf-8 -*-
"""
Blueprint for financial management endpoints.
"""

from flask import Blueprint, jsonify, request
from .models import db, Expense, Invoice, Payment
from .utils import token_required
from datetime import date

financial_bp = Blueprint('financial_bp', __name__)

@financial_bp.route('/expenses', methods=['POST'])
@token_required
def create_expense(current_user_id):
    """Create a new expense."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    data['submitted_by'] = current_user_id
    if 'expense_date' in data:
        data['expense_date'] = date.fromisoformat(data['expense_date'])
    expense = Expense(**data)
    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.to_dict()), 201

@financial_bp.route('/expenses/<expense_id>', methods=['GET'])
@token_required
def get_expense(current_user_id, expense_id):
    """Get an expense by ID."""
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify(expense.to_dict()), 200

@financial_bp.route('/invoices', methods=['POST'])
@token_required
def create_invoice(current_user_id):
    """Create a new invoice."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    data['created_by'] = current_user_id
    if 'issue_date' in data:
        data['issue_date'] = date.fromisoformat(data['issue_date'])
    if 'due_date' in data:
        data['due_date'] = date.fromisoformat(data['due_date'])
    invoice = Invoice(**data)
    db.session.add(invoice)
    db.session.commit()

    return jsonify(invoice.to_dict()), 201

@financial_bp.route('/invoices/<invoice_id>', methods=['GET'])
@token_required
def get_invoice(current_user_id, invoice_id):
    """Get an invoice by ID."""
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    return jsonify(invoice.to_dict()), 200

@financial_bp.route('/payments', methods=['POST'])
@token_required
def create_payment(current_user_id):
    """Create a new payment."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    payment = Payment(**data)
    db.session.add(payment)
    db.session.commit()

    return jsonify(payment.to_dict()), 201

@financial_bp.route('/payments/<payment_id>', methods=['GET'])
@token_required
def get_payment(current_user_id, payment_id):
    """Get a payment by ID."""
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    return jsonify(payment.to_dict()), 200
