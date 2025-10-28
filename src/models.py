from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
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

class User(db.Model):
    """User model for the application."""
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'))
    username = db.Column(db.String(64), unique=True, index=True, nullable=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(64))
    skills = db.Column(db.String(256))
    experience_years = db.Column(db.Integer)
    hourly_rate = db.Column(db.Integer)
    availability_hours_per_week = db.Column(db.Integer)
    location = db.Column(db.String(128))
    completion_rate = db.Column(db.Float)
    average_rating = db.Column(db.Float)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'user_type': self.user_type,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'hourly_rate': self.hourly_rate,
            'availability_hours_per_week': self.availability_hours_per_week,
            'location': self.location,
            'completion_rate': self.completion_rate,
            'average_rating': self.average_rating
        }

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'))
    name = db.Column(db.String(128))
    client_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    required_skills = db.Column(db.String(256))
    budget_max = db.Column(db.Integer)
    estimated_hours = db.Column(db.Integer)
    complexity_level = db.Column(db.Integer)
    urgency_level = db.Column(db.Integer)
    budget_used = db.Column(db.Integer)
    total_budget = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    progress_percentage = db.Column(db.Integer)
    open_bugs = db.Column(db.Integer)

    def __repr__(self):
        return '<Project %r>' % self.name

class Equity(db.Model):
    __tablename__ = 'equities'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    equity_percentage = db.Column(db.Float)

    def __repr__(self):
        return '<Equity %r>' % self.id

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    score = db.Column(db.Float)

    def __repr__(self):
        return '<Match %r>' % self.id

class AutomationRule(db.Model):
    __tablename__ = 'automation_rules'
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(128))
    trigger_type = db.Column(db.String(64))
    conditions = db.Column(db.JSON)
    actions = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    execution_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<AutomationRule %r>' % self.name

class SmartNotification(db.Model):
    __tablename__ = 'smart_notifications'
    id = db.Column(db.String(64), primary_key=True)
    recipient_id = db.Column(db.String(64))
    title = db.Column(db.String(128))
    message = db.Column(db.Text)
    priority = db.Column(db.String(64))
    notification_type = db.Column(db.String(64))
    data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)
    scheduled_for = db.Column(db.DateTime)

    def __repr__(self):
        return '<SmartNotification %r>' % self.id

class Expense(db.Model):
    """Expense tracking model"""
    __tablename__ = 'expenses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), nullable=False)
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
        """Convert expense to dictionary."""
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

class Organization(db.Model):
    """Organization model for multi-tenant support"""
    __tablename__ = 'organizations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text)

    # Organization settings stored as JSON
    settings = db.Column(db.Text, default='{}')

    # Organization status
    status = db.Column(db.String(50), default='active')  # active, suspended, inactive

    # Subscription and billing info
    subscription_plan = db.Column(db.String(100), default='basic')
    billing_email = db.Column(db.String(255))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='organization', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='organization', lazy=True, cascade='all, delete-orphan')
    roles = db.relationship('Role', backref='organization', lazy=True, cascade='all, delete-orphan')

    def __init__(self, name, domain=None, description=None, settings=None):
        self.name = name
        self.domain = domain
        self.description = description
        self.settings = json.dumps(settings or {})

    def get_settings(self):
        """Get organization settings as dictionary"""
        try:
            return json.loads(self.settings or '{}')
        except json.JSONDecodeError:
            return {}

    def set_settings(self, settings_dict):
        """Set organization settings from dictionary"""
        self.settings = json.dumps(settings_dict)

    def to_dict(self):
        """Convert organization to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'description': self.description,
            'settings': self.get_settings(),
            'status': self.status,
            'subscription_plan': self.subscription_plan,
            'billing_email': self.billing_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_count': len(self.users),
            'project_count': len(self.projects)
        }

    def __repr__(self):
        return f'<Organization {self.name}>'

class Role(db.Model):
    """Hierarchical role model with granular permissions"""
    __tablename__ = 'roles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)

    # Role details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Hierarchical structure
    parent_role_id = db.Column(db.String(36), db.ForeignKey('roles.id'))
    level = db.Column(db.Integer, default=0)

    # Permissions stored as JSON
    permissions = db.Column(db.Text, default='{}')

    # Role configuration
    is_system_role = db.Column(db.Boolean, default=False)  # System roles cannot be deleted
    is_active = db.Column(db.Boolean, default=True)
    max_subordinates = db.Column(db.Integer)  # Maximum number of direct subordinates

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential relationship for hierarchy
    children = db.relationship('Role', backref=db.backref('parent', remote_side=[id]), lazy=True)

    # Relationships
    user_roles = db.relationship('UserRole', backref='role', lazy=True, cascade='all, delete-orphan')

    def __init__(self, organization_id, name, description=None, parent_role_id=None, permissions=None):
        self.organization_id = organization_id
        self.name = name
        self.description = description
        self.parent_role_id = parent_role_id
        self.permissions = json.dumps(permissions or {})

        # Calculate level based on parent
        if parent_role_id:
            parent = Role.query.get(parent_role_id)
            if parent:
                self.level = parent.level + 1

    def get_permissions(self):
        """Get role permissions as dictionary"""
        try:
            return json.loads(self.permissions or '{}')
        except json.JSONDecodeError:
            return {}

    def set_permissions(self, permissions_dict):
        """Set role permissions from dictionary"""
        self.permissions = json.dumps(permissions_dict)

    def has_permission(self, resource, action):
        """Check if role has specific permission"""
        perms = self.get_permissions()
        resource_perms = perms.get(resource, {})
        return resource_perms.get(action, False)

    def add_permission(self, resource, action):
        """Add a specific permission to the role"""
        perms = self.get_permissions()
        if resource not in perms:
            perms[resource] = {}
        perms[resource][action] = True
        self.set_permissions(perms)

    def remove_permission(self, resource, action):
        """Remove a specific permission from the role"""
        perms = self.get_permissions()
        if resource in perms and action in perms[resource]:
            del perms[resource][action]
            if not perms[resource]:  # Remove empty resource
                del perms[resource]
            self.set_permissions(perms)

    def get_all_permissions(self):
        """Get all permissions including inherited from parent roles"""
        all_perms = {}

        # Start with current role permissions
        current_perms = self.get_permissions()
        all_perms.update(current_perms)

        # Add parent permissions (recursive)
        if self.parent:
            parent_perms = self.parent.get_all_permissions()
            for resource, actions in parent_perms.items():
                if resource not in all_perms:
                    all_perms[resource] = {}
                all_perms[resource].update(actions)

        return all_perms

    def get_subordinate_roles(self, include_indirect=True):
        """Get all subordinate roles"""
        subordinates = []

        # Direct children
        for child in self.children:
            subordinates.append(child)

            # Indirect children (recursive)
            if include_indirect:
                subordinates.extend(child.get_subordinate_roles(include_indirect=True))

        return subordinates

    def can_manage_role(self, target_role):
        """Check if this role can manage another role"""
        if not target_role:
            return False

        # Can manage if target is a subordinate
        subordinates = self.get_subordinate_roles(include_indirect=True)
        return target_role in subordinates

    def get_hierarchy_path(self):
        """Get the full hierarchy path from root to this role"""
        path = [self]
        current = self.parent

        while current:
            path.insert(0, current)
            current = current.parent

        return path

    def to_dict(self, include_hierarchy=False):
        """Convert role to dictionary"""
        result = {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'description': self.description,
            'parent_role_id': self.parent_role_id,
            'level': self.level,
            'permissions': self.get_permissions(),
            'is_system_role': self.is_system_role,
            'is_active': self.is_active,
            'max_subordinates': self.max_subordinates,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_count': len(self.user_roles),
            'children_count': len(self.children)
        }

        if include_hierarchy:
            result['parent'] = self.parent.to_dict() if self.parent else None
            result['children'] = [child.to_dict() for child in self.children]
            result['hierarchy_path'] = [role.name for role in self.get_hierarchy_path()]
            result['all_permissions'] = self.get_all_permissions()

        return result

    def __repr__(self):
        return f'<Role {self.name} (Level {self.level})>'

class UserRole(db.Model):
    """Association table for users and roles with additional metadata"""
    __tablename__ = 'user_roles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'), nullable=False)

    # Assignment metadata
    assigned_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Optional expiration

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Additional permissions or restrictions for this specific assignment
    additional_permissions = db.Column(db.Text, default='{}')
    restrictions = db.Column(db.Text, default='{}')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='user_roles')
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref='assigned_user_roles')

    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),)

    def __init__(self, user_id, role_id, assigned_by=None, expires_at=None):
        self.user_id = user_id
        self.role_id = role_id
        self.assigned_by = assigned_by
        self.expires_at = expires_at

    def get_additional_permissions(self):
        """Get additional permissions as dictionary"""
        try:
            return json.loads(self.additional_permissions or '{}')
        except json.JSONDecodeError:
            return {}

    def set_additional_permissions(self, permissions_dict):
        """Set additional permissions from dictionary"""
        self.additional_permissions = json.dumps(permissions_dict)

    def get_restrictions(self):
        """Get restrictions as dictionary"""
        try:
            return json.loads(self.restrictions or '{}')
        except json.JSONDecodeError:
            return {}

    def set_restrictions(self, restrictions_dict):
        """Set restrictions from dictionary"""
        self.restrictions = json.dumps(restrictions_dict)

    def is_expired(self):
        """Check if role assignment is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if role assignment is valid (active and not expired)"""
        return self.is_active and not self.is_expired()

    def to_dict(self):
        """Convert user role to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'assigned_by': self.assigned_by,
            'assigner_name': self.assigner.username if self.assigner else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid(),
            'additional_permissions': self.get_additional_permissions(),
            'restrictions': self.get_restrictions(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<UserRole {self.user_id} -> {self.role_id}>'

class Invoice(db.Model):
    """Invoice management model"""
    __tablename__ = 'invoices'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), nullable=False)
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
    organization_id = db.Column(db.String(36), nullable=False)
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
    payment_metadata = db.Column(db.Text, default='{}')  # JSON for gateway-specific data

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
            return json.loads(self.payment_metadata or '{}')
        except json.JSONDecodeError:
            return {}

    def set_metadata(self, metadata_dict):
        """Set metadata from dictionary"""
        self.payment_metadata = json.dumps(metadata_dict)

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
            payment_metadata = self.get_metadata()
            payment_metadata['failure_reason'] = reason
            self.set_metadata(payment_metadata)

    def refund(self, amount=None, reason=None):
        """Process refund"""
        self.status = PaymentStatus.REFUNDED
        if reason:
            payment_metadata = self.get_metadata()
            payment_metadata['refund_reason'] = reason
            payment_metadata['refund_amount'] = float(amount) if amount else float(self.amount)
            payment_metadata['refunded_at'] = datetime.utcnow().isoformat()
            self.set_metadata(payment_metadata)

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
            'payment_metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Payment {self.payment_reference} - {self.amount} {self.currency}>'

class Budget(db.Model):
    """Budget management model"""
    __tablename__ = 'budgets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    total_budget = db.Column(db.Numeric(15, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    # Relationships
    project = db.relationship('Project', backref='budgets')

    def __init__(self, project_id, total_budget, start_date, end_date):
        self.project_id = project_id
        self.total_budget = Decimal(str(total_budget))
        self.start_date = start_date
        self.end_date = end_date

    def to_dict(self):
        """Convert budget to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'total_budget': float(self.total_budget),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

    def __repr__(self):
        return f'<Budget {self.id} for Project {self.project_id}>'

class AIModel(db.Model):
    """AI Model management model"""
    __tablename__ = 'ai_models'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='development')

    # Relationships
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    project = db.relationship('Project', backref='ai_models')

    def __init__(self, name, description, version, project_id):
        self.name = name
        self.description = description
        self.version = version
        self.project_id = project_id

    def to_dict(self):
        """Convert AI model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'status': self.status,
            'project_id': self.project_id
        }

    def __repr__(self):
        return f'<AIModel {self.name} v{self.version}>'
