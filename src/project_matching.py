# -*- coding: utf-8 -*-
"""
AI-Powered Project Matching and Recommendation System for NeuraSynth
Provides intelligent matching between projects, team members, and resources
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Tuple
import json
import logging
from datetime import datetime, timedelta

class ProjectMatchingEngine:
    """
    Advanced AI engine for project matching and recommendations
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.project_vectors = None
        self.user_vectors = None
        self.skill_clusters = None
        self.logger = logging.getLogger(__name__)
        
    def extract_project_features(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant features from project data for matching
        """
        features = {
            'title': project.get('title', ''),
            'description': project.get('description', ''),
            'required_skills': project.get('required_skills', []),
            'budget_range': project.get('budget_range', 0),
            'duration_weeks': project.get('duration_weeks', 0),
            'complexity_level': project.get('complexity_level', 'medium'),
            'project_type': project.get('project_type', 'general'),
            'ai_model_type': project.get('ai_model_type', None),
            'industry': project.get('industry', 'technology'),
            'team_size': project.get('team_size', 1)
        }
        
        # Create combined text for vectorization
        text_features = f"{features['title']} {features['description']} {' '.join(features['required_skills'])} {features['project_type']} {features['industry']}"
        features['combined_text'] = text_features
        
        return features
    
    def extract_user_features(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant features from user data for matching
        """
        features = {
            'skills': user.get('skills', []),
            'experience_years': user.get('experience_years', 0),
            'specializations': user.get('specializations', []),
            'preferred_project_types': user.get('preferred_project_types', []),
            'availability_hours': user.get('availability_hours', 40),
            'hourly_rate': user.get('hourly_rate', 0),
            'rating': user.get('rating', 0),
            'completed_projects': user.get('completed_projects', 0),
            'preferred_industries': user.get('preferred_industries', []),
            'location': user.get('location', ''),
            'languages': user.get('languages', ['english'])
        }
        
        # Create combined text for vectorization
        text_features = f"{' '.join(features['skills'])} {' '.join(features['specializations'])} {' '.join(features['preferred_project_types'])} {' '.join(features['preferred_industries'])}"
        features['combined_text'] = text_features
        
        return features
    
    def calculate_skill_match_score(self, project_skills: List[str], user_skills: List[str]) -> float:
        """
        Calculate skill matching score between project requirements and user skills
        """
        if not project_skills or not user_skills:
            return 0.0
        
        project_skills_set = set([skill.lower() for skill in project_skills])
        user_skills_set = set([skill.lower() for skill in user_skills])
        
        intersection = project_skills_set.intersection(user_skills_set)
        union = project_skills_set.union(user_skills_set)
        
        if len(union) == 0:
            return 0.0
        
        jaccard_score = len(intersection) / len(union)
        coverage_score = len(intersection) / len(project_skills_set)
        
        # Weighted combination
        return 0.6 * jaccard_score + 0.4 * coverage_score
    
    def calculate_budget_compatibility(self, project_budget: float, user_rate: float, duration_weeks: int) -> float:
        """
        Calculate budget compatibility score
        """
        if project_budget <= 0 or user_rate <= 0:
            return 0.5  # Neutral score if budget info is missing
        
        estimated_cost = user_rate * 40 * duration_weeks  # Assuming 40 hours/week
        
        if estimated_cost <= project_budget:
            return 1.0
        elif estimated_cost <= project_budget * 1.2:  # 20% over budget
            return 0.8
        elif estimated_cost <= project_budget * 1.5:  # 50% over budget
            return 0.5
        else:
            return 0.2
    
    def calculate_experience_match(self, project_complexity: str, user_experience: int) -> float:
        """
        Calculate experience level matching
        """
        complexity_requirements = {
            'beginner': 0,
            'intermediate': 2,
            'advanced': 5,
            'expert': 8
        }
        
        required_experience = complexity_requirements.get(project_complexity.lower(), 2)
        
        if user_experience >= required_experience:
            return 1.0
        elif user_experience >= required_experience * 0.7:
            return 0.8
        elif user_experience >= required_experience * 0.5:
            return 0.6
        else:
            return 0.3
    
    def find_best_matches(self, project: Dict[str, Any], users: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find the best user matches for a given project
        """
        project_features = self.extract_project_features(project)
        matches = []
        
        for user in users:
            user_features = self.extract_user_features(user)
            
            # Calculate various matching scores
            skill_score = self.calculate_skill_match_score(
                project_features['required_skills'],
                user_features['skills']
            )
            
            budget_score = self.calculate_budget_compatibility(
                project_features['budget_range'],
                user_features['hourly_rate'],
                project_features['duration_weeks']
            )
            
            experience_score = self.calculate_experience_match(
                project_features['complexity_level'],
                user_features['experience_years']
            )
            
            # Text similarity using TF-IDF
            if hasattr(self, 'vectorizer') and self.vectorizer is not None:
                try:
                    project_vector = self.vectorizer.transform([project_features['combined_text']])
                    user_vector = self.vectorizer.transform([user_features['combined_text']])
                    text_similarity = cosine_similarity(project_vector, user_vector)[0][0]
                except:
                    text_similarity = 0.5
            else:
                text_similarity = 0.5
            
            # Rating and reliability score
            rating_score = min(user_features['rating'] / 5.0, 1.0) if user_features['rating'] > 0 else 0.5
            
            # Availability score
            availability_score = min(user_features['availability_hours'] / 40.0, 1.0)
            
            # Calculate weighted overall score
            overall_score = (
                0.25 * skill_score +
                0.20 * budget_score +
                0.15 * experience_score +
                0.15 * text_similarity +
                0.15 * rating_score +
                0.10 * availability_score
            )
            
            match_result = {
                'user_id': user.get('id'),
                'user_name': user.get('name', 'Unknown'),
                'overall_score': overall_score,
                'skill_score': skill_score,
                'budget_score': budget_score,
                'experience_score': experience_score,
                'text_similarity': text_similarity,
                'rating_score': rating_score,
                'availability_score': availability_score,
                'user_details': user_features
            }
            
            matches.append(match_result)
        
        # Sort by overall score and return top k
        matches.sort(key=lambda x: x['overall_score'], reverse=True)
        return matches[:top_k]
    
    def recommend_projects_for_user(self, user: Dict[str, Any], projects: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Recommend projects for a specific user
        """
        user_features = self.extract_user_features(user)
        recommendations = []
        
        for project in projects:
            project_features = self.extract_project_features(project)
            
            # Calculate matching scores (similar to find_best_matches but from user perspective)
            skill_score = self.calculate_skill_match_score(
                project_features['required_skills'],
                user_features['skills']
            )
            
            budget_score = self.calculate_budget_compatibility(
                project_features['budget_range'],
                user_features['hourly_rate'],
                project_features['duration_weeks']
            )
            
            experience_score = self.calculate_experience_match(
                project_features['complexity_level'],
                user_features['experience_years']
            )
            
            # Project type preference
            type_preference_score = 1.0 if project_features['project_type'] in user_features['preferred_project_types'] else 0.5
            
            # Industry preference
            industry_preference_score = 1.0 if project_features['industry'] in user_features['preferred_industries'] else 0.5
            
            # Calculate weighted overall score
            overall_score = (
                0.30 * skill_score +
                0.25 * budget_score +
                0.20 * experience_score +
                0.15 * type_preference_score +
                0.10 * industry_preference_score
            )
            
            recommendation = {
                'project_id': project.get('id'),
                'project_title': project.get('title', 'Unknown Project'),
                'overall_score': overall_score,
                'skill_score': skill_score,
                'budget_score': budget_score,
                'experience_score': experience_score,
                'type_preference_score': type_preference_score,
                'industry_preference_score': industry_preference_score,
                'project_details': project_features
            }
            
            recommendations.append(recommendation)
        
        # Sort by overall score and return top k
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        return recommendations[:top_k]
    
    def analyze_team_composition(self, project: Dict[str, Any], selected_users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the composition of a selected team for a project
        """
        project_features = self.extract_project_features(project)
        
        # Collect all skills from team members
        team_skills = set()
        total_experience = 0
        total_rate = 0
        skill_coverage = {}
        
        for user in selected_users:
            user_features = self.extract_user_features(user)
            team_skills.update([skill.lower() for skill in user_features['skills']])
            total_experience += user_features['experience_years']
            total_rate += user_features['hourly_rate']
            
            # Track skill coverage
            for skill in user_features['skills']:
                skill_lower = skill.lower()
                if skill_lower not in skill_coverage:
                    skill_coverage[skill_lower] = 0
                skill_coverage[skill_lower] += 1
        
        # Calculate metrics
        required_skills = set([skill.lower() for skill in project_features['required_skills']])
        skill_coverage_percentage = len(required_skills.intersection(team_skills)) / len(required_skills) if required_skills else 1.0
        
        avg_experience = total_experience / len(selected_users) if selected_users else 0
        avg_rate = total_rate / len(selected_users) if selected_users else 0
        
        estimated_cost = avg_rate * 40 * project_features['duration_weeks'] * len(selected_users)
        budget_efficiency = project_features['budget_range'] / estimated_cost if estimated_cost > 0 else 0
        
        # Identify skill gaps
        missing_skills = required_skills - team_skills
        redundant_skills = [skill for skill, count in skill_coverage.items() if count > 2]
        
        analysis = {
            'team_size': len(selected_users),
            'skill_coverage_percentage': skill_coverage_percentage,
            'missing_skills': list(missing_skills),
            'redundant_skills': redundant_skills,
            'average_experience': avg_experience,
            'average_hourly_rate': avg_rate,
            'estimated_total_cost': estimated_cost,
            'budget_efficiency': budget_efficiency,
            'recommendations': []
        }
        
        # Generate recommendations
        if skill_coverage_percentage < 0.8:
            analysis['recommendations'].append("Consider adding team members with missing skills")
        
        if budget_efficiency < 0.8:
            analysis['recommendations'].append("Team cost exceeds budget - consider optimization")
        
        if len(redundant_skills) > 0:
            analysis['recommendations'].append("Some skills are over-represented in the team")
        
        if avg_experience < 2 and project_features['complexity_level'] in ['advanced', 'expert']:
            analysis['recommendations'].append("Consider adding more experienced team members for this complex project")
        
        return analysis
    
    def train_matching_model(self, historical_projects: List[Dict[str, Any]], historical_users: List[Dict[str, Any]]):
        """
        Train the matching model using historical data
        """
        try:
            # Prepare text data for vectorization
            project_texts = []
            user_texts = []
            
            for project in historical_projects:
                features = self.extract_project_features(project)
                project_texts.append(features['combined_text'])
            
            for user in historical_users:
                features = self.extract_user_features(user)
                user_texts.append(features['combined_text'])
            
            # Train TF-IDF vectorizer
            all_texts = project_texts + user_texts
            if all_texts:
                self.vectorizer.fit(all_texts)
                self.logger.info(f"Trained TF-IDF vectorizer with {len(all_texts)} documents")
            
            # Create skill clusters for better matching
            all_skills = []
            for user in historical_users:
                all_skills.extend(user.get('skills', []))
            
            if all_skills:
                skill_texts = [' '.join(all_skills[i:i+5]) for i in range(0, len(all_skills), 5)]
                if len(skill_texts) > 5:
                    skill_vectors = self.vectorizer.transform(skill_texts)
                    self.skill_clusters = KMeans(n_clusters=min(10, len(skill_texts)//2))
                    self.skill_clusters.fit(skill_vectors.toarray())
                    self.logger.info("Created skill clusters for improved matching")
            
        except Exception as e:
            self.logger.error(f"Error training matching model: {str(e)}")
    
    def get_matching_insights(self, project: Dict[str, Any], users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get insights about the matching process for a project
        """
        project_features = self.extract_project_features(project)
        
        # Analyze user pool
        total_users = len(users)
        qualified_users = 0
        skill_distribution = {}
        experience_distribution = {'beginner': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
        
        for user in users:
            user_features = self.extract_user_features(user)
            
            # Check if user is qualified
            skill_match = self.calculate_skill_match_score(
                project_features['required_skills'],
                user_features['skills']
            )
            
            if skill_match > 0.3:  # Threshold for qualification
                qualified_users += 1
            
            # Track skill distribution
            for skill in user_features['skills']:
                skill_lower = skill.lower()
                if skill_lower not in skill_distribution:
                    skill_distribution[skill_lower] = 0
                skill_distribution[skill_lower] += 1
            
            # Track experience distribution
            exp_years = user_features['experience_years']
            if exp_years < 2:
                experience_distribution['beginner'] += 1
            elif exp_years < 5:
                experience_distribution['intermediate'] += 1
            elif exp_years < 8:
                experience_distribution['advanced'] += 1
            else:
                experience_distribution['expert'] += 1
        
        # Calculate insights
        qualification_rate = qualified_users / total_users if total_users > 0 else 0
        
        # Find most common skills in user pool
        top_skills = sorted(skill_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Check for rare skills
        required_skills_lower = [skill.lower() for skill in project_features['required_skills']]
        rare_skills = [skill for skill in required_skills_lower if skill_distribution.get(skill, 0) < 3]
        
        insights = {
            'total_users_in_pool': total_users,
            'qualified_users': qualified_users,
            'qualification_rate': qualification_rate,
            'top_skills_in_pool': top_skills,
            'rare_required_skills': rare_skills,
            'experience_distribution': experience_distribution,
            'matching_difficulty': 'high' if qualification_rate < 0.2 else 'medium' if qualification_rate < 0.5 else 'low',
            'recommendations': []
        }
        
        # Generate insights and recommendations
        if qualification_rate < 0.2:
            insights['recommendations'].append("Consider expanding the user pool or adjusting project requirements")
        
        if len(rare_skills) > 0:
            insights['recommendations'].append(f"Skills in high demand: {', '.join(rare_skills)}")
        
        if experience_distribution['expert'] < 2 and project_features['complexity_level'] == 'expert':
            insights['recommendations'].append("Limited expert-level users available for this complex project")
        
        return insights


class AIProjectRecommendationEngine:
    """
    AI-powered recommendation engine for project optimization and suggestions
    """
    
    def __init__(self):
        self.matching_engine = ProjectMatchingEngine()
        self.logger = logging.getLogger(__name__)
    
    def suggest_project_improvements(self, project: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest improvements to a project based on market data and best practices
        """
        suggestions = {
            'budget_optimization': [],
            'timeline_optimization': [],
            'skill_requirements': [],
            'market_positioning': [],
            'risk_mitigation': []
        }
        
        # Budget optimization suggestions
        market_avg_budget = market_data.get('average_budget_for_type', {}).get(project.get('project_type'), 0)
        if market_avg_budget > 0:
            current_budget = project.get('budget_range', 0)
            if current_budget > market_avg_budget * 1.3:
                suggestions['budget_optimization'].append("Budget is significantly above market average - consider optimization")
            elif current_budget < market_avg_budget * 0.7:
                suggestions['budget_optimization'].append("Budget may be too low for quality delivery - consider increase")
        
        # Timeline optimization
        market_avg_duration = market_data.get('average_duration_for_type', {}).get(project.get('project_type'), 0)
        if market_avg_duration > 0:
            current_duration = project.get('duration_weeks', 0)
            if current_duration < market_avg_duration * 0.8:
                suggestions['timeline_optimization'].append("Timeline may be too aggressive - consider extension")
        
        # Skill requirements analysis
        trending_skills = market_data.get('trending_skills', [])
        project_skills = project.get('required_skills', [])
        missing_trending = [skill for skill in trending_skills if skill not in project_skills]
        
        if missing_trending:
            suggestions['skill_requirements'].append(f"Consider adding trending skills: {', '.join(missing_trending[:3])}")
        
        # Market positioning
        similar_projects = market_data.get('similar_projects', [])
        if similar_projects:
            success_rate = sum(1 for p in similar_projects if p.get('status') == 'completed') / len(similar_projects)
            if success_rate < 0.7:
                suggestions['market_positioning'].append("Similar projects have lower success rates - consider differentiation")
        
        return suggestions
    
    def predict_project_success(self, project: Dict[str, Any], team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict the likelihood of project success based on various factors
        """
        factors = {
            'team_skill_match': 0,
            'budget_adequacy': 0,
            'timeline_realism': 0,
            'team_experience': 0,
            'project_complexity': 0
        }
        
        # Team skill match
        if team:
            project_features = self.matching_engine.extract_project_features(project)
            team_analysis = self.matching_engine.analyze_team_composition(project, team)
            factors['team_skill_match'] = team_analysis['skill_coverage_percentage']
            factors['budget_adequacy'] = min(team_analysis['budget_efficiency'], 1.0)
            factors['team_experience'] = min(team_analysis['average_experience'] / 5.0, 1.0)
        
        # Timeline realism (simplified heuristic)
        complexity_multipliers = {'beginner': 1.0, 'intermediate': 1.5, 'advanced': 2.0, 'expert': 3.0}
        expected_duration = project.get('team_size', 1) * complexity_multipliers.get(project.get('complexity_level', 'intermediate'), 1.5)
        actual_duration = project.get('duration_weeks', 1)
        factors['timeline_realism'] = min(expected_duration / actual_duration, 1.0) if actual_duration > 0 else 0.5
        
        # Project complexity assessment
        complexity_scores = {'beginner': 0.9, 'intermediate': 0.7, 'advanced': 0.5, 'expert': 0.3}
        factors['project_complexity'] = complexity_scores.get(project.get('complexity_level', 'intermediate'), 0.7)
        
        # Calculate overall success probability
        weights = {
            'team_skill_match': 0.3,
            'budget_adequacy': 0.2,
            'timeline_realism': 0.2,
            'team_experience': 0.15,
            'project_complexity': 0.15
        }
        
        success_probability = sum(factors[factor] * weights[factor] for factor in factors)
        
        # Generate risk factors and recommendations
        risk_factors = []
        recommendations = []
        
        if factors['team_skill_match'] < 0.7:
            risk_factors.append("Insufficient skill coverage in team")
            recommendations.append("Add team members with missing skills")
        
        if factors['budget_adequacy'] < 0.8:
            risk_factors.append("Budget may be insufficient")
            recommendations.append("Review and adjust budget or scope")
        
        if factors['timeline_realism'] < 0.7:
            risk_factors.append("Timeline may be too aggressive")
            recommendations.append("Consider extending timeline or reducing scope")
        
        return {
            'success_probability': success_probability,
            'confidence_level': 'high' if success_probability > 0.8 else 'medium' if success_probability > 0.6 else 'low',
            'factors': factors,
            'risk_factors': risk_factors,
            'recommendations': recommendations
        }


# Example usage and testing functions
def test_matching_engine():
    """
    Test function for the matching engine
    """
    # Sample project
    sample_project = {
        'id': 'proj_001',
        'title': 'AI Chatbot Development',
        'description': 'Develop an intelligent chatbot using NLP and machine learning',
        'required_skills': ['Python', 'NLP', 'Machine Learning', 'TensorFlow', 'API Development'],
        'budget_range': 50000,
        'duration_weeks': 12,
        'complexity_level': 'advanced',
        'project_type': 'ai_development',
        'industry': 'technology',
        'team_size': 3
    }
    
    # Sample users
    sample_users = [
        {
            'id': 'user_001',
            'name': 'Ahmed Hassan',
            'skills': ['Python', 'Machine Learning', 'TensorFlow', 'Deep Learning'],
            'experience_years': 6,
            'hourly_rate': 75,
            'rating': 4.8,
            'availability_hours': 40,
            'preferred_project_types': ['ai_development', 'data_science']
        },
        {
            'id': 'user_002',
            'name': 'Sara Mohamed',
            'skills': ['Python', 'NLP', 'API Development', 'Flask', 'Docker'],
            'experience_years': 4,
            'hourly_rate': 65,
            'rating': 4.6,
            'availability_hours': 35,
            'preferred_project_types': ['ai_development', 'backend_development']
        }
    ]
    
    # Test matching
    engine = ProjectMatchingEngine()
    matches = engine.find_best_matches(sample_project, sample_users)
    
    print("Project Matching Results:")
    for match in matches:
        print(f"User: {match['user_name']}, Score: {match['overall_score']:.3f}")
    
    return matches

if __name__ == "__main__":
    test_matching_engine()

