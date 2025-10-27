# -*- coding: utf-8 -*-
"""
Role Model for NeuraSynth Integrated System
Supports hierarchical roles with granular permissions
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import json

db = SQLAlchemy()

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
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref='assigned_roles')
    
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

# Default system roles and permissions
DEFAULT_SYSTEM_ROLES = {
    'super_admin': {
        'name': 'Super Administrator',
        'description': 'Full system access with all permissions',
        'permissions': {
            'organizations': {'create': True, 'read': True, 'update': True, 'delete': True, 'manage': True},
            'users': {'create': True, 'read': True, 'update': True, 'delete': True, 'manage': True},
            'roles': {'create': True, 'read': True, 'update': True, 'delete': True, 'manage': True},
            'projects': {'create': True, 'read': True, 'update': True, 'delete': True, 'manage': True},
            'contracts': {'create': True, 'read': True, 'update': True, 'delete': True, 'sign': True, 'manage': True},
            'finances': {'create': True, 'read': True, 'update': True, 'delete': True, 'approve': True, 'manage': True},
            'ai_models': {'create': True, 'read': True, 'update': True, 'delete': True, 'train': True, 'deploy': True, 'manage': True},
            'system': {'configure': True, 'monitor': True, 'backup': True, 'restore': True}
        }
    },
    'admin': {
        'name': 'Administrator',
        'description': 'Organization administrator with most permissions',
        'permissions': {
            'users': {'create': True, 'read': True, 'update': True, 'delete': True, 'manage': True},
            'roles': {'create': True, 'read': True, 'update': True, 'delete': False, 'manage': True},
            'projects': {'create': True, 'read': True, 'update': True, 'delete': True, 'manage': True},
            'contracts': {'create': True, 'read': True, 'update': True, 'delete': True, 'sign': True, 'manage': True},
            'finances': {'create': True, 'read': True, 'update': True, 'delete': False, 'approve': True, 'manage': True},
            'ai_models': {'create': True, 'read': True, 'update': True, 'delete': True, 'train': True, 'deploy': True, 'manage': True}
        }
    },
    'project_manager': {
        'name': 'Project Manager',
        'description': 'Manages projects and teams',
        'permissions': {
            'projects': {'create': True, 'read': True, 'update': True, 'delete': False, 'manage': True},
            'tasks': {'create': True, 'read': True, 'update': True, 'delete': True, 'assign': True},
            'users': {'read': True, 'update': False, 'assign': True},
            'contracts': {'read': True, 'update': False, 'create': False},
            'finances': {'read': True, 'create': True, 'update': False, 'approve': False},
            'ai_models': {'read': True, 'create': False, 'update': False, 'train': False, 'deploy': False}
        }
    },
    'ai_engineer': {
        'name': 'AI Engineer',
        'description': 'Develops and manages AI models',
        'permissions': {
            'ai_models': {'create': True, 'read': True, 'update': True, 'delete': False, 'train': True, 'deploy': True},
            'datasets': {'create': True, 'read': True, 'update': True, 'delete': False, 'validate': True},
            'experiments': {'create': True, 'read': True, 'update': True, 'delete': True},
            'projects': {'read': True, 'update': False},
            'tasks': {'read': True, 'update': True}
        }
    },
    'developer': {
        'name': 'Developer',
        'description': 'Software developer with code access',
        'permissions': {
            'projects': {'read': True, 'update': False},
            'tasks': {'read': True, 'update': True, 'create': False},
            'code': {'read': True, 'write': True, 'commit': True, 'review': True},
            'ai_models': {'read': True, 'update': False}
        }
    },
    'team_member': {
        'name': 'Team Member',
        'description': 'Basic team member with limited access',
        'permissions': {
            'projects': {'read': True},
            'tasks': {'read': True, 'update': True},
            'profile': {'read': True, 'update': True}
        }
    }
}

