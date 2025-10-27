# -*- coding: utf-8 -*-
"""
Organization Model for NeuraSynth Integrated System
Supports multi-tenant architecture with hierarchical organizations
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import json

db = SQLAlchemy()

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
    contracts = db.relationship('Contract', backref='organization', lazy=True, cascade='all, delete-orphan')
    
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

class OrganizationInvitation(db.Model):
    """Model for organization invitations"""
    __tablename__ = 'organization_invitations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'))
    
    # Invitation details
    invited_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    invitation_token = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, expired, cancelled
    
    # Expiration
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = db.relationship('Organization', backref='invitations')
    role = db.relationship('Role', backref='invitations')
    inviter = db.relationship('User', backref='sent_invitations')
    
    def __init__(self, organization_id, email, invited_by, role_id=None, expires_at=None):
        self.organization_id = organization_id
        self.email = email
        self.invited_by = invited_by
        self.role_id = role_id
        self.invitation_token = str(uuid.uuid4())
        
        if expires_at:
            self.expires_at = expires_at
        else:
            # Default expiration: 7 days from now
            from datetime import timedelta
            self.expires_at = datetime.utcnow() + timedelta(days=7)
    
    def is_expired(self):
        """Check if invitation is expired"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """Convert invitation to dictionary"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'organization_name': self.organization.name if self.organization else None,
            'email': self.email,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'invited_by': self.invited_by,
            'inviter_name': self.inviter.username if self.inviter else None,
            'invitation_token': self.invitation_token,
            'status': self.status,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OrganizationInvitation {self.email} to {self.organization.name if self.organization else "Unknown"}>'

