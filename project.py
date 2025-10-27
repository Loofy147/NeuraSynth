# -*- coding: utf-8 -*-
"""
NeuraSynth Studios - Project Manager
Simple project management for testing
"""

import uuid
import datetime

class ProjectManager:
    def __init__(self):
        self.projects = {}
    
    def create_project(self, data):
        try:
            project_id = str(uuid.uuid4())
            project = {
                'id': project_id,
                'created_at': datetime.datetime.utcnow().isoformat(),
                **data
            }
            self.projects[project_id] = project
            return {'success': True, 'project_id': project_id}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_project(self, project_id):
        return self.projects.get(project_id, None)

