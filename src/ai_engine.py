# -*- coding: utf-8 -*-
"""
NeuraSynth AI Engine Model
Advanced AI-powered matching and analytics system
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

db = SQLAlchemy()

class AIModel(db.Model):
    __tablename__ = 'ai_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # matching, prediction, recommendation
    
    # Model metadata
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)  # JSON string of model parameters
    performance_metrics = db.Column(db.Text)  # JSON string of performance metrics
    
    # Model file information
    model_path = db.Column(db.String(255))
    model_size = db.Column(db.Integer)  # in bytes
    
    # Status
    is_active = db.Column(db.Boolean, default=False)
    is_trained = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_trained = db.Column(db.DateTime)
    
    def get_parameters(self):
        """Get model parameters as a dictionary"""
        if self.parameters:
            try:
                return json.loads(self.parameters)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_parameters(self, params_dict):
        """Set model parameters from a dictionary"""
        self.parameters = json.dumps(params_dict)
    
    def get_performance_metrics(self):
        """Get performance metrics as a dictionary"""
        if self.performance_metrics:
            try:
                return json.loads(self.performance_metrics)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_performance_metrics(self, metrics_dict):
        """Set performance metrics from a dictionary"""
        self.performance_metrics = json.dumps(metrics_dict)
    
    def to_dict(self):
        """Convert AI model to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'model_type': self.model_type,
            'description': self.description,
            'parameters': self.get_parameters(),
            'performance_metrics': self.get_performance_metrics(),
            'model_path': self.model_path,
            'model_size': self.model_size,
            'is_active': self.is_active,
            'is_trained': self.is_trained,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_trained': self.last_trained.isoformat() if self.last_trained else None
        }

class MatchingResult(db.Model):
    __tablename__ = 'matching_results'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Matching scores
    overall_score = db.Column(db.Float, nullable=False)
    skill_match_score = db.Column(db.Float, default=0.0)
    experience_match_score = db.Column(db.Float, default=0.0)
    budget_match_score = db.Column(db.Float, default=0.0)
    availability_match_score = db.Column(db.Float, default=0.0)
    location_match_score = db.Column(db.Float, default=0.0)
    
    # AI analysis
    ai_analysis = db.Column(db.Text)  # JSON string of detailed AI analysis
    confidence_score = db.Column(db.Float, default=0.0)
    
    # Model information
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'))
    model_version = db.Column(db.String(20))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_ai_analysis(self):
        """Get AI analysis as a dictionary"""
        if self.ai_analysis:
            try:
                return json.loads(self.ai_analysis)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_ai_analysis(self, analysis_dict):
        """Set AI analysis from a dictionary"""
        self.ai_analysis = json.dumps(analysis_dict)
    
    def to_dict(self):
        """Convert matching result to dictionary for API responses"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'freelancer_id': self.freelancer_id,
            'overall_score': self.overall_score,
            'skill_match_score': self.skill_match_score,
            'experience_match_score': self.experience_match_score,
            'budget_match_score': self.budget_match_score,
            'availability_match_score': self.availability_match_score,
            'location_match_score': self.location_match_score,
            'ai_analysis': self.get_ai_analysis(),
            'confidence_score': self.confidence_score,
            'model_id': self.model_id,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AIMatchingEngine:
    """
    Advanced AI Matching Engine for NeuraSynth
    Implements sophisticated algorithms for project-freelancer matching
    """
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.matching_model = None
        self.is_trained = False
    
    def extract_text_features(self, text):
        """Extract text features using TF-IDF"""
        if not text:
            return np.zeros(1000)
        
        try:
            features = self.tfidf_vectorizer.transform([text])
            return features.toarray()[0]
        except:
            # If vectorizer is not fitted, return zeros
            return np.zeros(1000)
    
    def calculate_skill_match(self, project_skills, freelancer_skills):
        """Calculate skill matching score"""
        if not project_skills or not freelancer_skills:
            return 0.0
        
        # Convert to sets for intersection calculation
        project_set = set(project_skills) if isinstance(project_skills, list) else set()
        freelancer_set = set(freelancer_skills.keys()) if isinstance(freelancer_skills, dict) else set()
        
        if not project_set or not freelancer_set:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(project_set.intersection(freelancer_set))
        union = len(project_set.union(freelancer_set))
        
        if union == 0:
            return 0.0
        
        base_score = intersection / union
        
        # Boost score based on skill levels
        if isinstance(freelancer_skills, dict):
            level_boost = 0.0
            matched_skills = project_set.intersection(freelancer_set)
            for skill in matched_skills:
                level = freelancer_skills.get(skill, 'beginner')
                if level == 'expert':
                    level_boost += 0.3
                elif level == 'advanced':
                    level_boost += 0.2
                elif level == 'intermediate':
                    level_boost += 0.1
            
            level_boost = level_boost / len(matched_skills) if matched_skills else 0.0
            base_score = min(1.0, base_score + level_boost)
        
        return base_score
    
    def calculate_budget_match(self, project_budget_min, project_budget_max, freelancer_rate, estimated_hours=40):
        """Calculate budget matching score"""
        if not all([project_budget_min, project_budget_max, freelancer_rate]):
            return 0.5  # Neutral score if information is missing
        
        freelancer_total = freelancer_rate * estimated_hours
        project_avg = (project_budget_min + project_budget_max) / 2
        
        # Calculate how well the freelancer's rate fits the budget
        if freelancer_total <= project_budget_max and freelancer_total >= project_budget_min:
            # Perfect fit
            return 1.0
        elif freelancer_total < project_budget_min:
            # Under budget - good but might indicate lower quality
            ratio = freelancer_total / project_budget_min
            return 0.7 + (0.3 * ratio)
        else:
            # Over budget - penalize based on how much over
            if freelancer_total <= project_budget_max * 1.2:
                # Slightly over budget
                return 0.6
            elif freelancer_total <= project_budget_max * 1.5:
                # Moderately over budget
                return 0.3
            else:
                # Way over budget
                return 0.1
    
    def calculate_experience_match(self, project_experience_level, freelancer_projects_completed, freelancer_rating):
        """Calculate experience matching score"""
        if not project_experience_level:
            return 0.5  # Neutral if no requirement specified
        
        # Base score from completed projects
        if freelancer_projects_completed >= 50:
            projects_score = 1.0
        elif freelancer_projects_completed >= 20:
            projects_score = 0.8
        elif freelancer_projects_completed >= 10:
            projects_score = 0.6
        elif freelancer_projects_completed >= 5:
            projects_score = 0.4
        else:
            projects_score = 0.2
        
        # Rating boost
        rating_score = (freelancer_rating / 5.0) if freelancer_rating else 0.5
        
        # Combine scores
        base_score = (projects_score + rating_score) / 2
        
        # Adjust based on required experience level
        if project_experience_level == 'expert':
            if freelancer_projects_completed >= 30 and freelancer_rating >= 4.5:
                return base_score
            else:
                return base_score * 0.7
        elif project_experience_level == 'intermediate':
            if freelancer_projects_completed >= 10:
                return base_score
            else:
                return base_score * 0.8
        else:  # beginner
            return base_score
    
    def calculate_overall_match(self, project, freelancer):
        """Calculate overall matching score between project and freelancer"""
        # Extract features
        project_skills = project.get_required_skills() if hasattr(project, 'get_required_skills') else []
        freelancer_skills = freelancer.get_skills() if hasattr(freelancer, 'get_skills') else {}
        
        # Calculate individual scores
        skill_score = self.calculate_skill_match(project_skills, freelancer_skills)
        budget_score = self.calculate_budget_match(
            project.budget_min, 
            project.budget_max, 
            freelancer.hourly_rate
        )
        experience_score = self.calculate_experience_match(
            project.experience_level,
            freelancer.projects_completed,
            freelancer.average_rating
        )
        
        # Weighted combination
        weights = {
            'skill': 0.4,
            'budget': 0.3,
            'experience': 0.3
        }
        
        overall_score = (
            skill_score * weights['skill'] +
            budget_score * weights['budget'] +
            experience_score * weights['experience']
        )
        
        return {
            'overall_score': overall_score,
            'skill_match_score': skill_score,
            'budget_match_score': budget_score,
            'experience_match_score': experience_score,
            'confidence_score': min(skill_score, budget_score, experience_score)  # Lowest score as confidence
        }
    
    def find_best_matches(self, project, freelancers, limit=10):
        """Find best matching freelancers for a project"""
        matches = []
        
        for freelancer in freelancers:
            match_result = self.calculate_overall_match(project, freelancer)
            match_result['freelancer_id'] = freelancer.id
            match_result['freelancer'] = freelancer
            matches.append(match_result)
        
        # Sort by overall score
        matches.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return matches[:limit]
    
    def predict_project_success(self, project, freelancer):
        """Predict the likelihood of project success"""
        # This is a simplified prediction model
        # In a real implementation, this would use a trained ML model
        
        match_scores = self.calculate_overall_match(project, freelancer)
        
        # Factors that influence success
        factors = {
            'skill_match': match_scores['skill_match_score'] * 0.3,
            'experience': match_scores['experience_match_score'] * 0.25,
            'budget_fit': match_scores['budget_match_score'] * 0.2,
            'freelancer_rating': (freelancer.average_rating / 5.0) * 0.15,
            'freelancer_completion_rate': min(1.0, freelancer.projects_completed / 10) * 0.1
        }
        
        success_probability = sum(factors.values())
        return min(1.0, success_probability)
    
    def generate_recommendations(self, user, user_type='freelancer'):
        """Generate AI-powered recommendations for users"""
        recommendations = {
            'skill_improvements': [],
            'profile_optimizations': [],
            'market_insights': [],
            'pricing_suggestions': []
        }
        
        if user_type == 'freelancer':
            # Skill improvement recommendations
            user_skills = user.get_skills() if hasattr(user, 'get_skills') else {}
            if len(user_skills) < 5:
                recommendations['skill_improvements'].append(
                    "Consider adding more skills to your profile to increase matching opportunities"
                )
            
            # Profile optimization
            if not user.bio or len(user.bio) < 100:
                recommendations['profile_optimizations'].append(
                    "Add a detailed bio to improve your profile completeness"
                )
            
            if not user.portfolio_url:
                recommendations['profile_optimizations'].append(
                    "Add a portfolio URL to showcase your work"
                )
            
            # Pricing suggestions
            if user.hourly_rate and user.hourly_rate < 10:
                recommendations['pricing_suggestions'].append(
                    "Consider increasing your hourly rate based on your skills and experience"
                )
        
        return recommendations

