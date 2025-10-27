# -*- coding: utf-8 -*-
"""
NeuraSynth Enhanced User Model
Comprehensive user management with AI-powered features and contributor hub
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class UserType(Enum):
    CLIENT = "client"
    FREELANCER = "freelancer"
    BOTH = "both"
    CONTRIBUTOR = "contributor"
    ADMIN = "admin"

class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    timezone = db.Column(db.String(50))
    language = db.Column(db.String(10), default='en')
    
    # User type and verification
    user_type = db.Column(db.Enum(UserType), default=UserType.FREELANCER)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Professional information
    title = db.Column(db.String(100))
    hourly_rate = db.Column(db.Float)
    currency = db.Column(db.String(3), default='USD')
    availability = db.Column(db.String(20))  # full-time, part-time, contract
    
    # Skills and experience
    skills = db.Column(db.Text)  # JSON string of skills with levels
    portfolio_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    
    # AI-powered features
    ai_profile_score = db.Column(db.Float, default=0.0)
    ai_recommendations = db.Column(db.Text)  # JSON string of AI recommendations
    matching_preferences = db.Column(db.Text)  # JSON string of matching preferences
    
    # Contributors Hub features
    is_contributor = db.Column(db.Boolean, default=False)
    contribution_score = db.Column(db.Float, default=0.0)
    total_earnings = db.Column(db.Float, default=0.0)
    contributor_level = db.Column(db.String(20), default='bronze')  # bronze, silver, gold, platinum
    
    # Statistics
    projects_completed = db.Column(db.Integer, default=0)
    total_earned = db.Column(db.Float, default=0.0)
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    projects_created = db.relationship('Project', foreign_keys='Project.client_id', backref='client', lazy=True)
    applications = db.relationship('ProjectApplication', foreign_keys='ProjectApplication.freelancer_id', backref='freelancer', lazy=True)
    contributions = db.relationship('Contribution', backref='contributor', lazy=True)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.skills and isinstance(self.skills, dict):
            self.skills = json.dumps(self.skills)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_skills(self):
        """Get skills as a dictionary"""
        if self.skills:
            try:
                return json.loads(self.skills)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_skills(self, skills_dict):
        """Set skills from a dictionary"""
        self.skills = json.dumps(skills_dict)
    
    def get_ai_recommendations(self):
        """Get AI recommendations as a dictionary"""
        if self.ai_recommendations:
            try:
                return json.loads(self.ai_recommendations)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_ai_recommendations(self, recommendations_dict):
        """Set AI recommendations from a dictionary"""
        self.ai_recommendations = json.dumps(recommendations_dict)
    
    def get_matching_preferences(self):
        """Get matching preferences as a dictionary"""
        if self.matching_preferences:
            try:
                return json.loads(self.matching_preferences)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_matching_preferences(self, preferences_dict):
        """Set matching preferences from a dictionary"""
        self.matching_preferences = json.dumps(preferences_dict)
    
    def calculate_contributor_level(self):
        """Calculate contributor level based on contribution score"""
        if self.contribution_score >= 1000:
            return 'platinum'
        elif self.contribution_score >= 500:
            return 'gold'
        elif self.contribution_score >= 100:
            return 'silver'
        else:
            return 'bronze'
    
    def update_contributor_level(self):
        """Update contributor level based on current score"""
        self.contributor_level = self.calculate_contributor_level()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for API responses"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'location': self.location,
            'timezone': self.timezone,
            'language': self.language,
            'user_type': self.user_type.value if self.user_type else None,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'title': self.title,
            'hourly_rate': self.hourly_rate,
            'currency': self.currency,
            'availability': self.availability,
            'skills': self.get_skills(),
            'portfolio_url': self.portfolio_url,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'ai_profile_score': self.ai_profile_score,
            'ai_recommendations': self.get_ai_recommendations(),
            'matching_preferences': self.get_matching_preferences(),
            'is_contributor': self.is_contributor,
            'contribution_score': self.contribution_score,
            'total_earnings': self.total_earnings,
            'contributor_level': self.contributor_level,
            'projects_completed': self.projects_completed,
            'total_earned': self.total_earned,
            'average_rating': self.average_rating,
            'total_reviews': self.total_reviews,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        return data

class Contribution(db.Model):
    __tablename__ = 'contributions'
    
    id = db.Column(db.Integer, primary_key=True)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Contribution details
    type = db.Column(db.String(50), nullable=False)  # code, design, content, testing, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Contribution value
    impact_score = db.Column(db.Float, default=0.0)
    quality_score = db.Column(db.Float, default=0.0)
    innovation_score = db.Column(db.Float, default=0.0)
    total_score = db.Column(db.Float, default=0.0)
    
    # Rewards
    reward_amount = db.Column(db.Float, default=0.0)
    reward_currency = db.Column(db.String(3), default='USD')
    is_rewarded = db.Column(db.Boolean, default=False)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    def calculate_total_score(self):
        """Calculate total contribution score"""
        self.total_score = (self.impact_score + self.quality_score + self.innovation_score) / 3
        return self.total_score
    
    def to_dict(self):
        """Convert contribution to dictionary for API responses"""
        return {
            'id': self.id,
            'contributor_id': self.contributor_id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'impact_score': self.impact_score,
            'quality_score': self.quality_score,
            'innovation_score': self.innovation_score,
            'total_score': self.total_score,
            'reward_amount': self.reward_amount,
            'reward_currency': self.reward_currency,
            'is_rewarded': self.is_rewarded,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }

