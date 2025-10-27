# -*- coding: utf-8 -*-
"""
NeuraSynth Studios - Contributors Hub
Simple contributors hub for testing
"""

class ContributorsHub:
    def __init__(self):
        self.equity_data = {}
        self.performance_data = {}
    
    def get_equity_holdings(self, contributor_id):
        return self.equity_data.get(contributor_id, {
            'equity_percentage': 0.0,
            'vesting_schedule': {},
            'granted_date': None
        })
    
    def get_performance_metrics(self, contributor_id):
        return self.performance_data.get(contributor_id, {
            'projects_completed': 0,
            'average_rating': 0.0,
            'total_earnings': 0.0
        })

