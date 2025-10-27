from .models import db, User, Project, Match
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
    """

    def __init__(self):
        """
        Initialize the advanced matching engine
        """
        self.feature_weights = {
            'skill_similarity': 0.35,
            'experience_match': 0.25,
            'budget_compatibility': 0.20,
            'availability_match': 0.10,
            'location_preference': 0.05,
            'success_prediction': 0.05
        }
        self.skill_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.success_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()

    def extract_features(self, freelancer_data, project_data):
        """
        Extract features for matching calculation
        """
        features = {}

        try:
            freelancer_skills = ' '.join(freelancer_data.get('skills', []))
            project_skills = ' '.join(project_data.get('required_skills', []))

            if freelancer_skills and project_skills:
                skill_vectors = self.skill_vectorizer.transform([freelancer_skills, project_skills])
                skill_similarity = cosine_similarity(skill_vectors[0:1], skill_vectors[1:2])[0][0]
            else:
                skill_similarity = 0.0

            features['skill_similarity'] = skill_similarity

            freelancer_experience = freelancer_data.get('experience_years', 0)
            project_complexity = project_data.get('complexity_level', 1)

            required_experience = project_complexity * 2
            experience_match = min(freelancer_experience / max(required_experience, 1), 1.0)

            features['experience_match'] = experience_match

            freelancer_rate = freelancer_data.get('hourly_rate', 0)
            project_budget_max = project_data.get('budget_max', 0)
            estimated_hours = project_data.get('estimated_hours', 40)

            if freelancer_rate > 0 and project_budget_max > 0 and estimated_hours > 0:
                estimated_cost = freelancer_rate * estimated_hours
                budget_compatibility = min(project_budget_max / estimated_cost, 1.0)
            else:
                budget_compatibility = 0.5

            features['budget_compatibility'] = budget_compatibility

            freelancer_availability = freelancer_data.get('availability_hours_per_week', 40)
            project_urgency = project_data.get('urgency_level', 1)

            required_availability = project_urgency * 10
            availability_match = min(freelancer_availability / max(required_availability, 1), 1.0)

            features['availability_match'] = availability_match

            freelancer_location = freelancer_data.get('location', '')
            project_location = project_data.get('location', '')

            if freelancer_location and project_location:
                location_match = 1.0 if freelancer_location == project_location else 0.5
            else:
                location_match = 0.7

            features['location_preference'] = location_match

            try:
                budget_adequacy = features['budget_compatibility']
                timeline_realism = 1.0 - (project_data.get('urgency_level', 1) - 1) * 0.2
                skill_match = features['skill_similarity']
                freelancer_reliability = freelancer_data.get('completion_rate', 0.8)
                project_clarity = 0.8

                prediction_features = np.array([[
                    budget_adequacy, timeline_realism, skill_match,
                    freelancer_reliability, project_clarity
                ]])

                prediction_features_scaled = self.scaler.transform(prediction_features)
                success_prediction = self.success_model.predict(prediction_features_scaled)[0]
                success_prediction = max(0, min(1, success_prediction))

            except Exception as e:
                success_prediction = 0.7

            features['success_prediction'] = success_prediction

        except Exception as e:
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
        """
        try:
            features = self.extract_features(freelancer_data, project_data)

            total_score = 0.0
            for feature_name, weight in self.feature_weights.items():
                feature_value = features.get(feature_name, 0.0)
                total_score += feature_value * weight

            total_score = max(0.0, min(1.0, total_score))

            return total_score

        except Exception as e:
            return 0.0

    def find_matches_for_project(self, project_id, max_matches=10):
        """
        Find best freelancer matches for a given project
        """
        try:
            project = Project.query.get(project_id)
            if not project:
                return []

            project_data = {
                'required_skills': project.required_skills.split(','),
                'budget_max': project.budget_max,
                'estimated_hours': project.estimated_hours,
                'complexity_level': project.complexity_level,
                'urgency_level': project.urgency_level
            }

            freelancers = User.query.filter_by(user_type='freelancer').all()
            matches = []

            for freelancer in freelancers:
                freelancer_data = {
                    'skills': freelancer.skills.split(','),
                    'experience_years': freelancer.experience_years,
                    'hourly_rate': freelancer.hourly_rate,
                    'availability_hours_per_week': freelancer.availability_hours_per_week,
                    'location': freelancer.location,
                    'completion_rate': freelancer.completion_rate,
                    'average_rating': freelancer.average_rating
                }

                match_score = self.calculate_match_score(freelancer_data, project_data)

                match = Match(project_id=project_id, user_id=freelancer.id, score=match_score)
                db.session.add(match)

                matches.append({
                    'freelancer_id': freelancer.id,
                    'match_score': match_score
                })

            db.session.commit()

            matches.sort(key=lambda x: x['match_score'], reverse=True)

            return matches[:max_matches]

        except Exception as e:
            return []
