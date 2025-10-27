from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for the application."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
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

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))
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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    equity_percentage = db.Column(db.Float)

    def __repr__(self):
        return '<Equity %r>' % self.id

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
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
