from .models import db, Project

class ProjectManager:
    def create_project(self, data):
        project = Project(**data)
        db.session.add(project)
        db.session.commit()
        return {'success': True, 'project_id': project.id}

    def get_project(self, project_id):
        project = Project.query.get(project_id)
        if project:
            return {
                'id': project.id,
                'name': project.name,
                'client_id': project.client_id
            }
        return None
