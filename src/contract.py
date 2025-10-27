# -*- coding: utf-8 -*-
"""
Contract Model for NeuraSynth Integrated System
Supports comprehensive contract lifecycle management
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import json
from enum import Enum

db = SQLAlchemy()

class ContractType(Enum):
    """Contract type enumeration"""
    SERVICE = "service"
    EMPLOYMENT = "employment"
    PARTNERSHIP = "partnership"
    NDA = "nda"
    LICENSING = "licensing"
    CONSULTING = "consulting"
    MAINTENANCE = "maintenance"
    CUSTOM = "custom"

class ContractStatus(Enum):
    """Contract status enumeration"""
    DRAFT = "draft"
    REVIEW = "review"
    NEGOTIATION = "negotiation"
    APPROVED = "approved"
    SIGNED = "signed"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Contract(db.Model):
    """Comprehensive contract model"""
    __tablename__ = 'contracts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'))
    
    # Contract identification
    contract_number = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Contract classification
    type = db.Column(db.Enum(ContractType), default=ContractType.CUSTOM)
    status = db.Column(db.Enum(ContractStatus), default=ContractStatus.DRAFT)
    
    # Financial terms
    value = db.Column(db.Numeric(15, 2))
    currency = db.Column(db.String(3), default='USD')
    payment_terms = db.Column(db.Text)  # JSON with payment schedule
    
    # Timeline
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    duration_months = db.Column(db.Integer)
    
    # Contract terms and conditions
    terms = db.Column(db.Text, default='{}')  # JSON with detailed terms
    deliverables = db.Column(db.Text, default='[]')  # JSON array of deliverables
    milestones = db.Column(db.Text, default='[]')  # JSON array of milestones
    
    # Parties involved
    parties = db.Column(db.Text, default='[]')  # JSON array of contract parties
    
    # Legal and compliance
    governing_law = db.Column(db.String(100))
    jurisdiction = db.Column(db.String(100))
    
    # Document management
    documents = db.Column(db.Text, default='[]')  # JSON array of document references
    template_id = db.Column(db.String(36))  # Reference to contract template
    
    # Workflow and approvals
    approval_workflow = db.Column(db.Text, default='[]')  # JSON array of approval steps
    current_approver = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Signatures
    signature_required = db.Column(db.Boolean, default=True)
    signatures = db.Column(db.Text, default='[]')  # JSON array of signatures
    
    # Renewal and termination
    auto_renewal = db.Column(db.Boolean, default=False)
    renewal_notice_days = db.Column(db.Integer, default=30)
    termination_notice_days = db.Column(db.Integer, default=30)
    
    # Risk and compliance
    risk_level = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    compliance_requirements = db.Column(db.Text, default='[]')  # JSON array
    
    # Metadata
    metadata = db.Column(db.Text, default='{}')
    tags = db.Column(db.Text, default='[]')
    
    # Audit trail
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    last_modified_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    signed_at = db.Column(db.DateTime)
    activated_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_contracts')
    modifier = db.relationship('User', foreign_keys=[last_modified_by], backref='modified_contracts')
    approver = db.relationship('User', foreign_keys=[current_approver], backref='pending_approvals')
    
    def __init__(self, title, organization_id, created_by, **kwargs):
        self.title = title
        self.organization_id = organization_id
        self.created_by = created_by
        
        # Generate unique contract number if not provided
        if 'contract_number' not in kwargs:
            self.contract_number = self.generate_contract_number()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_contract_number(self):
        """Generate unique contract number"""
        import random
        import string
        
        # Format: CT-YYYY-XXXX (e.g., CT-2024-A1B2)
        year = datetime.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"CT-{year}-{random_part}"
    
    def get_terms(self):
        """Get terms as dictionary"""
        try:
            return json.loads(self.terms or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_terms(self, terms_dict):
        """Set terms from dictionary"""
        self.terms = json.dumps(terms_dict)
    
    def get_deliverables(self):
        """Get deliverables as list"""
        try:
            return json.loads(self.deliverables or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_deliverables(self, deliverables_list):
        """Set deliverables from list"""
        self.deliverables = json.dumps(deliverables_list)
    
    def get_milestones(self):
        """Get milestones as list"""
        try:
            return json.loads(self.milestones or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_milestones(self, milestones_list):
        """Set milestones from list"""
        self.milestones = json.dumps(milestones_list)
    
    def get_parties(self):
        """Get parties as list"""
        try:
            return json.loads(self.parties or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_parties(self, parties_list):
        """Set parties from list"""
        self.parties = json.dumps(parties_list)
    
    def get_documents(self):
        """Get documents as list"""
        try:
            return json.loads(self.documents or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_documents(self, documents_list):
        """Set documents from list"""
        self.documents = json.dumps(documents_list)
    
    def get_signatures(self):
        """Get signatures as list"""
        try:
            return json.loads(self.signatures or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_signatures(self, signatures_list):
        """Set signatures from list"""
        self.signatures = json.dumps(signatures_list)
    
    def get_approval_workflow(self):
        """Get approval workflow as list"""
        try:
            return json.loads(self.approval_workflow or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_approval_workflow(self, workflow_list):
        """Set approval workflow from list"""
        self.approval_workflow = json.dumps(workflow_list)
    
    def get_payment_terms(self):
        """Get payment terms as dictionary"""
        try:
            return json.loads(self.payment_terms or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_payment_terms(self, payment_terms_dict):
        """Set payment terms from dictionary"""
        self.payment_terms = json.dumps(payment_terms_dict)
    
    def get_metadata(self):
        """Get metadata as dictionary"""
        try:
            return json.loads(self.metadata or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_metadata(self, metadata_dict):
        """Set metadata from dictionary"""
        self.metadata = json.dumps(metadata_dict)
    
    def get_tags(self):
        """Get tags as list"""
        try:
            return json.loads(self.tags or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_tags(self, tags_list):
        """Set tags from list"""
        self.tags = json.dumps(tags_list)
    
    def is_expired(self):
        """Check if contract is expired"""
        if not self.end_date:
            return False
        return datetime.now().date() > self.end_date
    
    def is_active(self):
        """Check if contract is currently active"""
        return self.status == ContractStatus.ACTIVE and not self.is_expired()
    
    def days_until_expiry(self):
        """Get days until contract expiry"""
        if not self.end_date:
            return None
        delta = self.end_date - datetime.now().date()
        return delta.days if delta.days > 0 else 0
    
    def needs_renewal_notice(self):
        """Check if renewal notice is needed"""
        if not self.auto_renewal or not self.end_date:
            return False
        days_until_expiry = self.days_until_expiry()
        return days_until_expiry <= self.renewal_notice_days
    
    def can_be_signed(self):
        """Check if contract can be signed"""
        return self.status == ContractStatus.APPROVED and self.signature_required
    
    def add_signature(self, user_id, signature_data):
        """Add a signature to the contract"""
        signatures = self.get_signatures()
        signature = {
            'user_id': user_id,
            'signed_at': datetime.utcnow().isoformat(),
            'signature_data': signature_data,
            'ip_address': signature_data.get('ip_address'),
            'user_agent': signature_data.get('user_agent')
        }
        signatures.append(signature)
        self.set_signatures(signatures)
        
        # Check if all required signatures are collected
        if self.all_signatures_collected():
            self.status = ContractStatus.SIGNED
            self.signed_at = datetime.utcnow()
    
    def all_signatures_collected(self):
        """Check if all required signatures are collected"""
        signatures = self.get_signatures()
        parties = self.get_parties()
        
        # Simple check: number of signatures >= number of parties requiring signature
        required_signatures = len([p for p in parties if p.get('requires_signature', True)])
        return len(signatures) >= required_signatures
    
    def activate(self):
        """Activate the contract"""
        if self.status == ContractStatus.SIGNED:
            self.status = ContractStatus.ACTIVE
            self.activated_at = datetime.utcnow()
    
    def complete(self):
        """Mark contract as completed"""
        if self.status == ContractStatus.ACTIVE:
            self.status = ContractStatus.COMPLETED
            self.completed_at = datetime.utcnow()
    
    def terminate(self, reason=None):
        """Terminate the contract"""
        self.status = ContractStatus.TERMINATED
        if reason:
            metadata = self.get_metadata()
            metadata['termination_reason'] = reason
            metadata['terminated_at'] = datetime.utcnow().isoformat()
            self.set_metadata(metadata)
    
    def to_dict(self, include_details=False):
        """Convert contract to dictionary"""
        result = {
            'id': self.id,
            'organization_id': self.organization_id,
            'project_id': self.project_id,
            'contract_number': self.contract_number,
            'title': self.title,
            'description': self.description,
            'type': self.type.value if self.type else None,
            'status': self.status.value if self.status else None,
            'value': float(self.value) if self.value else None,
            'currency': self.currency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration_months': self.duration_months,
            'governing_law': self.governing_law,
            'jurisdiction': self.jurisdiction,
            'template_id': self.template_id,
            'current_approver': self.current_approver,
            'signature_required': self.signature_required,
            'auto_renewal': self.auto_renewal,
            'renewal_notice_days': self.renewal_notice_days,
            'termination_notice_days': self.termination_notice_days,
            'risk_level': self.risk_level,
            'created_by': self.created_by,
            'last_modified_by': self.last_modified_by,
            'is_expired': self.is_expired(),
            'is_active': self.is_active(),
            'days_until_expiry': self.days_until_expiry(),
            'needs_renewal_notice': self.needs_renewal_notice(),
            'can_be_signed': self.can_be_signed(),
            'all_signatures_collected': self.all_signatures_collected(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'activated_at': self.activated_at.isoformat() if self.activated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_details:
            result.update({
                'terms': self.get_terms(),
                'deliverables': self.get_deliverables(),
                'milestones': self.get_milestones(),
                'parties': self.get_parties(),
                'documents': self.get_documents(),
                'payment_terms': self.get_payment_terms(),
                'approval_workflow': self.get_approval_workflow(),
                'signatures': self.get_signatures(),
                'compliance_requirements': json.loads(self.compliance_requirements or '[]'),
                'metadata': self.get_metadata(),
                'tags': self.get_tags(),
                'creator': self.creator.to_dict() if self.creator else None,
                'modifier': self.modifier.to_dict() if self.modifier else None,
                'approver': self.approver.to_dict() if self.approver else None
            })
        
        return result
    
    def __repr__(self):
        return f'<Contract {self.contract_number} - {self.title}>'

class ContractTemplate(db.Model):
    """Contract template for standardization"""
    __tablename__ = 'contract_templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    
    # Template details
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    
    # Template content
    template_content = db.Column(db.Text, nullable=False)  # HTML/Markdown template
    default_terms = db.Column(db.Text, default='{}')  # JSON with default terms
    required_fields = db.Column(db.Text, default='[]')  # JSON array of required fields
    optional_fields = db.Column(db.Text, default='[]')  # JSON array of optional fields
    
    # Template configuration
    is_active = db.Column(db.Boolean, default=True)
    is_system_template = db.Column(db.Boolean, default=False)
    version = db.Column(db.String(20), default='1.0')
    
    # Usage tracking
    usage_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='contract_templates')
    
    def __init__(self, name, template_content, organization_id, created_by, **kwargs):
        self.name = name
        self.template_content = template_content
        self.organization_id = organization_id
        self.created_by = created_by
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_default_terms(self):
        """Get default terms as dictionary"""
        try:
            return json.loads(self.default_terms or '{}')
        except json.JSONDecodeError:
            return {}
    
    def set_default_terms(self, terms_dict):
        """Set default terms from dictionary"""
        self.default_terms = json.dumps(terms_dict)
    
    def get_required_fields(self):
        """Get required fields as list"""
        try:
            return json.loads(self.required_fields or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_required_fields(self, fields_list):
        """Set required fields from list"""
        self.required_fields = json.dumps(fields_list)
    
    def get_optional_fields(self):
        """Get optional fields as list"""
        try:
            return json.loads(self.optional_fields or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_optional_fields(self, fields_list):
        """Set optional fields from list"""
        self.optional_fields = json.dumps(fields_list)
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
    
    def to_dict(self):
        """Convert template to dictionary"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'template_content': self.template_content,
            'default_terms': self.get_default_terms(),
            'required_fields': self.get_required_fields(),
            'optional_fields': self.get_optional_fields(),
            'is_active': self.is_active,
            'is_system_template': self.is_system_template,
            'version': self.version,
            'usage_count': self.usage_count,
            'created_by': self.created_by,
            'creator': self.creator.to_dict() if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ContractTemplate {self.name} v{self.version}>'

