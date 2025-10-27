# -*- coding: utf-8 -*-
"""
Financial Model for NeuraSynth Integrated System
Supports comprehensive financial management including expenses, invoices, payments
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import json
from enum import Enum
from decimal import Decimal

db = SQLAlchemy()

class ExpenseCategory(Enum):
    """Expense category enumeration"""
    DEVELOPMENT = "development"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    INFRASTRUCTURE = "infrastructure"
    LEGAL = "legal"
    TRAVEL = "travel"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    CONSULTING = "consulting"
    OTHER = "other"

class ExpenseStatus(Enum):
    """Expense status enumeration"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class InvoiceStatus(Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Expense(db.Model):
    """Expense tracking model"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    
    # Expense details
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.Enum(ExpenseCategory), default=ExpenseCategory.OTHER)
    
    # Financial information
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2))
    
    # Expense metadata
    expense_date = db.Column(db.Date, nullable=False)
    vendor = db.Column(db.String(255))
    receipt_number = db.Column(db.String(100))
    
    # Status and approval
    status = db.Column(db.Enum(ExpenseStatus), default=ExpenseStatus.DRAFT)
    submitted_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    # Attachments and documentation
    attachments = db.Column(db.Text, default='[]')  # JSON array of file references
    notes = db.Column(db.Text)
    
    # Reimbursement
    is_reimbursable = db.Column(db.Boolean, default=True)
    reimbursed_amount = db.Column(db.Numeric(15, 2), default=0)
    reimbursed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submitter = db.relationship('User', foreign_keys=[submitted_by], backref='submitted_expenses')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_expenses')
    
    def __init__(self, title, amount, expense_date, submitted_by, organization_id, **kwargs):
        self.title = title
        self.amount = Decimal(str(amount))
        self.expense_date = expense_date
        self.submitted_by = submitted_by
        self.organization_id = organization_id
        
        # Calculate total amount
        tax_amount = kwargs.get('tax_amount', 0)
        self.tax_amount = Decimal(str(tax_amount))
        self.total_amount = self.amount + self.tax_amount
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['amount', 'tax_amount']:
                setattr(self, key, value)
    
    def get_attachments(self):
        """Get attachments as list"""
        try:
            return json.loads(self.attachments or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_attachments(self, attachments_list):
        """Set attachments from list"""
        self.attachments = json.dumps(attachments_list)
    
    def add_attachment(self, attachment):
        """Add an attachment"""
        attachments = self.get_attachments()
        attachments.append(attachment)
        self.set_attachments(attachments)
    
    def approve(self, approved_by_user_id):
        """Approve the expense"""
        self.status = ExpenseStatus.APPROVED
        self.approved_by = approved_by_user_id
        self.approved_at = datetime.utcnow()
    
    def reject(self, reason=None):
        """Reject the expense"""
        self.status = ExpenseStatus.REJECTED
        if reason:
            self.notes = f"{self.notes or ''}\nRejection reason: {reason}"
    
    def mark_paid(self, amount=None):
        """Mark expense as paid"""
        self.status = ExpenseStatus.PAID
        if amount:
            self.reimbursed_amount = Decimal(str(amount))
        else:
            self.reimbursed_amount = self.total_amount
        self.reimbursed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert expense to dictionary"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'amount': float(self.amount),
            'currency': self.currency,
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'vendor': self.vendor,
            'receipt_number': self.receipt_number,
            'status': self.status.value if self.status else None,
            'submitted_by': self.submitted_by,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'attachments': self.get_attachments(),
            'notes': self.notes,
            'is_reimbursable': self.is_reimbursable,
            'reimbursed_amount': float(self.reimbursed_amount),
            'reimbursed_at': self.reimbursed_at.isoformat() if self.reimbursed_at else None,
            'submitter': self.submitter.to_dict() if self.submitter else None,
            'approver': self.approver.to_dict() if self.approver else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Expense {self.title} - {self.amount} {self.currency}>'

class Invoice(db.Model):
    """Invoice management model"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    
    # Invoice identification
    invoice_number = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Financial details
    subtotal = db.Column(db.Numeric(15, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 4), default=0)  # e.g., 0.1500 for 15%
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Client information
    client_name = db.Column(db.String(255), nullable=False)
    client_email = db.Column(db.String(255))
    client_address = db.Column(db.Text)
    client_tax_id = db.Column(db.String(100))
    
    # Invoice timeline
    issue_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date)
    
    # Status and tracking
    status = db.Column(db.Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    sent_at = db.Column(db.DateTime)
    viewed_at = db.Column(db.DateTime)
    
    # Payment information
    payment_terms = db.Column(db.String(255))
    payment_method = db.Column(db.String(100))
    payment_reference = db.Column(db.String(255))
    
    # Line items
    line_items = db.Column(db.Text, default='[]')  # JSON array of line items
    
    # Notes and terms
    notes = db.Column(db.Text)
    terms_and_conditions = db.Column(db.Text)
    
    # Created by
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_invoices')
    
    def __init__(self, invoice_number, title, subtotal, client_name, issue_date, due_date, created_by, organization_id, **kwargs):
        self.invoice_number = invoice_number
        self.title = title
        self.subtotal = Decimal(str(subtotal))
        self.client_name = client_name
        self.issue_date = issue_date
        self.due_date = due_date
        self.created_by = created_by
        self.organization_id = organization_id
        
        # Calculate amounts
        self.tax_rate = Decimal(str(kwargs.get('tax_rate', 0)))
        self.discount_amount = Decimal(str(kwargs.get('discount_amount', 0)))
        self.tax_amount = (self.subtotal - self.discount_amount) * self.tax_rate
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['subtotal', 'tax_rate', 'discount_amount']:
                setattr(self, key, value)
    
    def get_line_items(self):
        """Get line items as list"""
        try:
            return json.loads(self.line_items or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_line_items(self, items_list):
        """Set line items from list"""
        self.line_items = json.dumps(items_list)
        # Recalculate subtotal
        self.subtotal = sum(Decimal(str(item.get('total', 0))) for item in items_list)
        self.recalculate_total()
    
    def add_line_item(self, item):
        """Add a line item"""
        items = self.get_line_items()
        items.append(item)
        self.set_line_items(items)
    
    def recalculate_total(self):
        """Recalculate total amount"""
        self.tax_amount = (self.subtotal - self.discount_amount) * self.tax_rate
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
    
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            return False
        return datetime.now().date() > self.due_date
    
    def days_overdue(self):
        """Get number of days overdue"""
        if not self.is_overdue():
            return 0
        return (datetime.now().date() - self.due_date).days
    
    def mark_sent(self):
        """Mark invoice as sent"""
        self.status = InvoiceStatus.SENT
        self.sent_at = datetime.utcnow()
    
    def mark_viewed(self):
        """Mark invoice as viewed"""
        if self.status == InvoiceStatus.SENT:
            self.status = InvoiceStatus.VIEWED
        self.viewed_at = datetime.utcnow()
    
    def mark_paid(self, payment_date=None, payment_reference=None):
        """Mark invoice as paid"""
        self.status = InvoiceStatus.PAID
        self.paid_date = payment_date or datetime.now().date()
        if payment_reference:
            self.payment_reference = payment_reference
    
    def to_dict(self):
        """Convert invoice to dictionary"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'project_id': self.project_id,
            'invoice_number': self.invoice_number,
            'title': self.title,
            'description': self.description,
            'subtotal': float(self.subtotal),
            'tax_rate': float(self.tax_rate),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'client_address': self.client_address,
            'client_tax_id': self.client_tax_id,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'status': self.status.value if self.status else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'payment_terms': self.payment_terms,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'line_items': self.get_line_items(),
            'notes': self.notes,
            'terms_and_conditions': self.terms_and_conditions,
            'created_by': self.created_by,
            'is_overdue': self.is_overdue(),
            'days_overdue': self.days_overdue(),
            'creator': self.creator.to_dict() if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number} - {self.total_amount} {self.currency}>'

class Payment(db.Model):
    """Payment tracking model"""
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id'))
    
    # Payment details
    payment_reference = db.Column(db.String(255), unique=True, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Payment method and gateway
    payment_method = db.Column(db.String(100), nullable=False)  # credit_card, bank_transfer, paypal, etc.
    gateway = db.Column(db.String(100))  # stripe, paypal, bank, etc.
    gateway_transaction_id = db.Column(db.String(255))
    
    # Status and timeline
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Payer information
    payer_name = db.Column(db.String(255))
    payer_email = db.Column(db.String(255))
    payer_reference = db.Column(db.String(255))
    
    # Fees and charges
    gateway_fee = db.Column(db.Numeric(10, 2), default=0)
    processing_fee = db.Column(db.Numeric(10, 2), default=0)
    net_amount = db.Column(db.Numeric(15, 2))
    
    # Additional information
    description = db.Column(db.Text)
    metadata = db.Column(db.Text, default='{}')  # JSON for gateway-specific data
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = db.relationship('Invoice', backref='payments')
    
    def __init__(self, payment_reference, amount, payment_method, organization_id, **kwargs):
        self.payment_reference = payment_reference
        self.amount = Decimal(str(amount))
        self.payment_method = payment_method
        self.organization_id = organization_id
        
        # Calculate net amount
        gateway_fee = kwargs.get('gateway_fee', 0)
        processing_fee = kwargs.get('processing_fee', 0)
        self.gateway_fee = Decimal(str(gateway_fee))
        self.processing_fee = Decimal(str(processing_fee))
        self.net_amount = self.amount - self.gateway_fee - self.processing_fee
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['amount', 'gateway_fee', 'processing_fee']:
                setattr(self, key, value)
    
    def get_metadata(self):
        """Get metadata as dictionary"""
        try:
            return json.loads(self.metadata or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_metadata(self, metadata_dict):
        """Set metadata from dictionary"""
        self.metadata = json.dumps(metadata_dict)
    
    def mark_completed(self, gateway_transaction_id=None):
        """Mark payment as completed"""
        self.status = PaymentStatus.COMPLETED
        self.processed_at = datetime.utcnow()
        if gateway_transaction_id:
            self.gateway_transaction_id = gateway_transaction_id
    
    def mark_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        if reason:
            metadata = self.get_metadata()
            metadata['failure_reason'] = reason
            self.set_metadata(metadata)
    
    def refund(self, amount=None, reason=None):
        """Process refund"""
        self.status = PaymentStatus.REFUNDED
        if reason:
            metadata = self.get_metadata()
            metadata['refund_reason'] = reason
            metadata['refund_amount'] = float(amount) if amount else float(self.amount)
            metadata['refunded_at'] = datetime.utcnow().isoformat()
            self.set_metadata(metadata)
    
    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'invoice_id': self.invoice_id,
            'payment_reference': self.payment_reference,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'gateway': self.gateway,
            'gateway_transaction_id': self.gateway_transaction_id,
            'status': self.status.value if self.status else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'payer_name': self.payer_name,
            'payer_email': self.payer_email,
            'payer_reference': self.payer_reference,
            'gateway_fee': float(self.gateway_fee),
            'processing_fee': float(self.processing_fee),
            'net_amount': float(self.net_amount),
            'description': self.description,
            'metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Payment {self.payment_reference} - {self.amount} {self.currency}>'

class Budget(db.Model):
    """Budget management model"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    
    # Budget details
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Budget period
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Budget amounts
    total_budget = db.Column(db.Numeric(15, 2), nullable=False)
    allocated_amount = db.Column(db.Numeric(15, 2), default=0)
    spent_amount = db.Column(db.Numeric(15, 2), default=0)
    remaining_amount = db.Column(db.Numeric(15, 2))
    currency = db.Column(db.String(3), default='USD')
    
    # Budget categories
    categories = db.Column(db.Text, default='{}')  # JSON with category allocations
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Created by
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_budgets')
    
    def __init__(self, name, total_budget, start_date, end_date, created_by, organization_id, **kwargs):
        self.name = name
        self.total_budget = Decimal(str(total_budget))
        self.start_date = start_date
        self.end_date = end_date
        self.created_by = created_by
        self.organization_id = organization_id
        self.remaining_amount = self.total_budget
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'total_budget':
                setattr(self, key, value)
    
    def get_categories(self):
        """Get categories as dictionary"""
        try:
            return json.loads(self.categories or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_categories(self, categories_dict):
        """Set categories from dictionary"""
        self.categories = json.dumps(categories_dict)
    
    def update_spent_amount(self):
        """Update spent amount based on expenses"""
        # This would calculate from related expenses
        # For now, keep the current value
        self.remaining_amount = self.total_budget - self.spent_amount
    
    def get_utilization_percentage(self):
        """Get budget utilization percentage"""
        if self.total_budget == 0:
            return 0
        return float((self.spent_amount / self.total_budget) * 100)
    
    def is_over_budget(self):
        """Check if over budget"""
        return self.spent_amount > self.total_budget
    
    def to_dict(self):
        """Convert budget to dictionary"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_budget': float(self.total_budget),
            'allocated_amount': float(self.allocated_amount),
            'spent_amount': float(self.spent_amount),
            'remaining_amount': float(self.remaining_amount),
            'currency': self.currency,
            'categories': self.get_categories(),
            'is_active': self.is_active,
            'created_by': self.created_by,
            'utilization_percentage': self.get_utilization_percentage(),
            'is_over_budget': self.is_over_budget(),
            'creator': self.creator.to_dict() if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Budget {self.name} - {self.total_budget} {self.currency}>'

