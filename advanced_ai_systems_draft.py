# -*- coding: utf-8 -*-
"""
NeuraSynth Studios - Advanced AI Matching Engine
Orchestrator-AI Production Unit - AI/ML Core System

This module implements the core AI/ML algorithms for matching freelancers with projects
using advanced machine learning techniques including TF-IDF, cosine similarity,
and predictive analytics.

⚠️ SUSPICIOUS POINT: Model training data should be from real database
⚠️ SUSPICIOUS POINT: Feature weights should be configurable
⚠️ SUSPICIOUS POINT: Performance optimization needed for large datasets
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import json
import datetime
import uuid

class AdvancedMatchingEngine:
    """
    Advanced AI-powered matching engine for NeuraSynth Studios
    
    Uses machine learning algorithms to match freelancers with projects
    based on multiple factors including skills, experience, budget, and success prediction.
    """
    
    def __init__(self):
        """
        Initialize the advanced matching engine
        
        # ESSENTIAL STEP: Set up ML models and feature extractors
        """
        # Feature weights for matching algorithm
        # ⚠️ SUSPICIOUS POINT: These should be configurable and tunable
        self.feature_weights = {
            'skill_similarity': 0.35,
            'experience_match': 0.25,
            'budget_compatibility': 0.20,
            'availability_match': 0.10,
            'location_preference': 0.05,
            'success_prediction': 0.05
        }
        
        # Initialize TF-IDF vectorizer for skill matching
        self.skill_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Initialize success prediction model
        self.success_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        
        # Feature scaler for numerical features
        self.scaler = StandardScaler()
        
        # In-memory storage for demo (replace with database in production)
        # ⚠️ SUSPICIOUS POINT: This should be replaced with proper database
        self.freelancers_db = {}
        self.projects_db = {}
        self.matches_db = {}
        
        # Initialize with demo data
        self._initialize_demo_data()
        
        # Train models with demo data
        self._train_models()
    
    def _initialize_demo_data(self):
        """
        Initialize demo freelancers and projects for testing
        
        # ESSENTIAL STEP: Remove this in production
        ⚠️ SUSPICIOUS POINT: Demo data should not exist in production
        """
        # Demo freelancers
        demo_freelancers = [
            {
                'id': str(uuid.uuid4()),
                'name': 'أحمد محمد',
                'skills': ['Python', 'Machine Learning', 'Data Science', 'Flask'],
                'experience_years': 5,
                'hourly_rate': 50,
                'availability_hours_per_week': 40,
                'location': 'Cairo, Egypt',
                'completion_rate': 0.95,
                'average_rating': 4.8,
                'projects_completed': 25
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'فاطمة أحمد',
                'skills': ['React', 'JavaScript', 'Node.js', 'UI/UX Design'],
                'experience_years': 3,
                'hourly_rate': 40,
                'availability_hours_per_week': 35,
                'location': 'Dubai, UAE',
                'completion_rate': 0.92,
                'average_rating': 4.6,
                'projects_completed': 18
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'محمد علي',
                'skills': ['Python', 'React', 'Full Stack Development', 'DevOps'],
                'experience_years': 7,
                'hourly_rate': 65,
                'availability_hours_per_week': 30,
                'location': 'Riyadh, Saudi Arabia',
                'completion_rate': 0.98,
                'average_rating': 4.9,
                'projects_completed': 42
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'سارة خالد',
                'skills': ['AI', 'Deep Learning', 'TensorFlow', 'Computer Vision'],
                'experience_years': 4,
                'hourly_rate': 55,
                'availability_hours_per_week': 40,
                'location': 'Amman, Jordan',
                'completion_rate': 0.94,
                'average_rating': 4.7,
                'projects_completed': 22
            }
        ]
        
        for freelancer in demo_freelancers:
            self.freelancers_db[freelancer['id']] = freelancer
        
        # Demo projects
        demo_projects = [
            {
                'id': str(uuid.uuid4()),
                'title': 'E-commerce Website Development',
                'description': 'Need a modern e-commerce platform with React frontend and Python backend',
                'required_skills': ['React', 'Python', 'E-commerce', 'Database'],
                'budget_min': 2000,
                'budget_max': 5000,
                'estimated_hours': 100,
                'complexity_level': 3,
                'urgency_level': 2,
                'deadline': '2024-03-15'
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'AI Chatbot Development',
                'description': 'Develop an intelligent chatbot using machine learning and NLP',
                'required_skills': ['AI', 'Machine Learning', 'NLP', 'Python'],
                'budget_min': 3000,
                'budget_max': 7000,
                'estimated_hours': 120,
                'complexity_level': 4,
                'urgency_level': 3,
                'deadline': '2024-02-28'
            }
        ]
        
        for project in demo_projects:
            self.projects_db[project['id']] = project
    
    def _train_models(self):
        """
        Train ML models with available data
        
        # ESSENTIAL STEP: Train models for accurate predictions
        ⚠️ SUSPICIOUS POINT: Need more training data for better accuracy
        """
        try:
            # Prepare training data for success prediction
            training_data = []
            
            # Generate synthetic training data based on demo data
            # ⚠️ SUSPICIOUS POINT: This should use real historical data
            for _ in range(100):
                # Synthetic features
                budget_adequacy = np.random.uniform(0.5, 1.0)
                timeline_realism = np.random.uniform(0.6, 1.0)
                skill_match = np.random.uniform(0.4, 1.0)
                freelancer_reliability = np.random.uniform(0.7, 1.0)
                project_clarity = np.random.uniform(0.5, 1.0)
                
                # Calculate synthetic success score
                success_score = (
                    budget_adequacy * 0.25 +
                    timeline_realism * 0.20 +
                    skill_match * 0.25 +
                    freelancer_reliability * 0.20 +
                    project_clarity * 0.10
                ) + np.random.normal(0, 0.1)  # Add some noise
                
                success_score = max(0, min(1, success_score))  # Clamp to [0, 1]
                
                training_data.append([
                    budget_adequacy, timeline_realism, skill_match,
                    freelancer_reliability, project_clarity, success_score
                ])
            
            # Convert to DataFrame
            df = pd.DataFrame(training_data, columns=[
                'budget_adequacy', 'timeline_realism', 'skill_match',
                'freelancer_reliability', 'project_clarity', 'success_score'
            ])
            
            # Prepare features and target
            X = df[['budget_adequacy', 'timeline_realism', 'skill_match',
                   'freelancer_reliability', 'project_clarity']]
            y = df['success_score']
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train success prediction model
            self.success_model.fit(X_scaled, y)
            
            # Prepare skill corpus for TF-IDF
            skill_corpus = []
            for freelancer in self.freelancers_db.values():
                skill_corpus.append(' '.join(freelancer['skills']))
            
            for project in self.projects_db.values():
                skill_corpus.append(' '.join(project['required_skills']))
            
            # Fit TF-IDF vectorizer
            if skill_corpus:
                self.skill_vectorizer.fit(skill_corpus)
            
        except Exception as e:
            # ⚠️ SUSPICIOUS POINT: Better error handling needed
            print(f"Warning: Model training failed: {e}")
    
    def extract_features(self, freelancer_data, project_data):
        """
        Extract features for matching calculation
        
        Args:
            freelancer_data (dict): Freelancer information
            project_data (dict): Project information
        
        Returns:
            dict: Extracted features
        
        # ESSENTIAL STEP: Extract all relevant features for matching
        """
        features = {}
        
        try:
            # 1. Skill similarity using TF-IDF and cosine similarity
            freelancer_skills = ' '.join(freelancer_data.get('skills', []))
            project_skills = ' '.join(project_data.get('required_skills', []))
            
            if freelancer_skills and project_skills:
                skill_vectors = self.skill_vectorizer.transform([freelancer_skills, project_skills])
                skill_similarity = cosine_similarity(skill_vectors[0:1], skill_vectors[1:2])[0][0]
            else:
                skill_similarity = 0.0
            
            features['skill_similarity'] = skill_similarity
            
            # 2. Experience match
            freelancer_experience = freelancer_data.get('experience_years', 0)
            project_complexity = project_data.get('complexity_level', 1)
            
            # Calculate experience adequacy
            required_experience = project_complexity * 2  # Rough heuristic
            experience_match = min(freelancer_experience / max(required_experience, 1), 1.0)
            
            features['experience_match'] = experience_match
            
            # 3. Budget compatibility
            freelancer_rate = freelancer_data.get('hourly_rate', 0)
            project_budget_max = project_data.get('budget_max', 0)
            estimated_hours = project_data.get('estimated_hours', 40)
            
            if freelancer_rate > 0 and project_budget_max > 0 and estimated_hours > 0:
                estimated_cost = freelancer_rate * estimated_hours
                budget_compatibility = min(project_budget_max / estimated_cost, 1.0)
            else:
                budget_compatibility = 0.5  # Neutral if data missing
            
            features['budget_compatibility'] = budget_compatibility
            
            # 4. Availability match
            freelancer_availability = freelancer_data.get('availability_hours_per_week', 40)
            project_urgency = project_data.get('urgency_level', 1)
            
            # Higher urgency requires more availability
            required_availability = project_urgency * 10  # Rough heuristic
            availability_match = min(freelancer_availability / max(required_availability, 1), 1.0)
            
            features['availability_match'] = availability_match
            
            # 5. Location preference (simplified)
            # ⚠️ SUSPICIOUS POINT: This is very basic, needs improvement
            freelancer_location = freelancer_data.get('location', '')
            project_location = project_data.get('location', '')
            
            if freelancer_location and project_location:
                # Simple string matching (should be improved with geolocation)
                location_match = 1.0 if freelancer_location == project_location else 0.5
            else:
                location_match = 0.7  # Neutral for remote work
            
            features['location_preference'] = location_match
            
            # 6. Success prediction using ML model
            try:
                # Prepare features for success prediction
                budget_adequacy = features['budget_compatibility']
                timeline_realism = 1.0 - (project_data.get('urgency_level', 1) - 1) * 0.2
                skill_match = features['skill_similarity']
                freelancer_reliability = freelancer_data.get('completion_rate', 0.8)
                project_clarity = 0.8  # Assume reasonable clarity
                
                prediction_features = np.array([[
                    budget_adequacy, timeline_realism, skill_match,
                    freelancer_reliability, project_clarity
                ]])
                
                prediction_features_scaled = self.scaler.transform(prediction_features)
                success_prediction = self.success_model.predict(prediction_features_scaled)[0]
                success_prediction = max(0, min(1, success_prediction))  # Clamp to [0, 1]
                
            except Exception as e:
                # ⚠️ SUSPICIOUS POINT: Better error handling needed
                success_prediction = 0.7  # Default value
            
            features['success_prediction'] = success_prediction
            
        except Exception as e:
            # ⚠️ SUSPICIOUS POINT: Better error handling needed
            print(f"Warning: Feature extraction failed: {e}")
            # Return default features
            features = {
                'skill_similarity': 0.5,
                'experience_match': 0.5,
                'budget_compatibility': 0.5,
                'availability_match': 0.5,
                'location_preference': 0.5,
                'success_prediction': 0.5
            }
        
        return features
    
    def calculate_match_score(self, freelancer_data, project_data):
        """
        Calculate overall match score between freelancer and project
        
        Args:
            freelancer_data (dict): Freelancer information
            project_data (dict): Project information
        
        Returns:
            float: Match score between 0 and 1
        
        # ESSENTIAL STEP: Combine all features with appropriate weights
        """
        try:
            # Extract features
            features = self.extract_features(freelancer_data, project_data)
            
            # Calculate weighted score
            total_score = 0.0
            for feature_name, weight in self.feature_weights.items():
                feature_value = features.get(feature_name, 0.0)
                total_score += feature_value * weight
            
            # Ensure score is between 0 and 1
            total_score = max(0.0, min(1.0, total_score))
            
            return total_score
            
        except Exception as e:
            # ⚠️ SUSPICIOUS POINT: Better error handling needed
            print(f"Warning: Match score calculation failed: {e}")
            return 0.0
    
    def find_matches_for_project(self, project_id, max_matches=10):
        """
        Find best freelancer matches for a given project
        
        Args:
            project_id (str): Project ID
            max_matches (int): Maximum number of matches to return
        
        Returns:
            list: List of match results sorted by score
        
        # ESSENTIAL STEP: Return ranked list of best matches
        """
        try:
            # Get project data
            if project_id not in self.projects_db:
                # ⚠️ SUSPICIOUS POINT: Should query actual database
                return []
            
            project_data = self.projects_db[project_id]
            matches = []
            
            # Calculate match scores for all freelancers
            for freelancer_id, freelancer_data in self.freelancers_db.items():
                # Extract features
                features = self.extract_features(freelancer_data, project_data)
                
                # Calculate overall match score
                match_score = self.calculate_match_score(freelancer_data, project_data)
                
                # Create match result
                match_result = {
                    'freelancer_id': freelancer_id,
                    'match_score': round(match_score, 3),
                    'skill_similarity': round(features['skill_similarity'], 3),
                    'experience_match': round(features['experience_match'], 3),
                    'budget_compatibility': round(features['budget_compatibility'], 3),
                    'success_prediction': round(features['success_prediction'], 3),
                    'freelancer_profile': {
                        'name': freelancer_data.get('name', 'Unknown'),
                        'skills': freelancer_data.get('skills', []),
                        'experience_years': freelancer_data.get('experience_years', 0),
                        'hourly_rate': freelancer_data.get('hourly_rate', 0),
                        'average_rating': freelancer_data.get('average_rating', 0),
                        'completion_rate': freelancer_data.get('completion_rate', 0)
                    }
                }
                
                matches.append(match_result)
            
            # Sort by match score (descending)
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Store matches in database for future reference
            # ⚠️ SUSPICIOUS POINT: Should store in actual database
            self.matches_db[project_id] = {
                'project_id': project_id,
                'matches': matches[:max_matches],
                'generated_at': datetime.datetime.utcnow().isoformat()
            }
            
            return matches[:max_matches]
            
        except Exception as e:
            # ⚠️ SUSPICIOUS POINT: Better error handling needed
            print(f"Error finding matches: {e}")
            return []
    
    def get_stored_matches(self, project_id):
        """
        Get previously calculated matches for a project
        
        Args:
            project_id (str): Project ID
        
        Returns:
            list: Stored match results or empty list
        
        # ESSENTIAL STEP: Retrieve cached matches efficiently
        """
        try:
            if project_id in self.matches_db:
                return self.matches_db[project_id]['matches']
            else:
                return []
        except Exception as e:
            # ⚠️ SUSPICIOUS POINT: Better error handling needed
            return []
    
    def update_feature_weights(self, new_weights):
        """
        Update feature weights for matching algorithm
        
        Args:
            new_weights (dict): New feature weights
        
        Returns:
            bool: Success status
        
        # ESSENTIAL STEP: Allow dynamic weight adjustment
        ⚠️ SUSPICIOUS POINT: Need validation for weight values
        """
        try:
            # Validate weights
            total_weight = sum(new_weights.values())
            if abs(total_weight - 1.0) > 0.01:  # Allow small tolerance
                return False
            
            # Update weights
            self.feature_weights.update(new_weights)
            return True
            
        except Exception as e:
            # ⚠️ SUSPICIOUS POINT: Better error handling needed
            return False

