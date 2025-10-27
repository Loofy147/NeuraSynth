from flask import request, jsonify
from . import projects
from ..project import ProjectManager
from ..utils import ai_matching_engine, token_required
from ..automation_blueprint import automation_engine
import asyncio

project_manager = ProjectManager()

@projects.route('/create', methods=['POST'])
@token_required
def create_project(current_user_id):
    """
    Create a new project
    """
    try:
        data = request.get_json()

        # Add client_id to project data
        data['client_id'] = current_user_id

        # Create project
        result = project_manager.create_project(data)

        if result['success']:
            project_id = result['project_id']

            # Trigger project creation event
            asyncio.run(automation_engine.trigger_event(
                'project_created',
                {'project_id': project_id, 'client_id': current_user_id}
            ))

            # Trigger AI matching for the new project
            try:
                matches = ai_matching_engine.find_matches_for_project(project_id)

                return jsonify({
                    'success': True,
                    'project_id': project_id,
                    'ai_matches': matches[:5],  # Return top 5 matches
                    'message': 'Project created successfully'
                }), 201

            except Exception as matching_error:
                # Project created but matching failed
                return jsonify({
                    'success': True,
                    'project_id': project_id,
                    'ai_matches': [],
                    'message': 'Project created but AI matching failed',
                    'matching_error': str(matching_error)
                }), 201
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f'Failed to create project: {str(e)}'}), 500

@projects.route('/<project_id>', methods=['GET'])
@token_required
def get_project(current_user_id, project_id):
    """
    Get project details
    """
    try:
        project_data = project_manager.get_project(project_id)

        if project_data:
            return jsonify({
                'success': True,
                'project': project_data
            }), 200
        else:
            return jsonify({'error': 'Project not found'}), 404

    except Exception as e:
        return jsonify({'error': f'Failed to get project: {str(e)}'}), 500

@projects.route('/<project_id>/matches', methods=['GET'])
@token_required
def find_matches(current_user_id, project_id):
    """
    Find AI-powered matches for a project
    """
    try:
        import datetime
        start_time = datetime.datetime.utcnow()

        # Get matches using AI engine
        matches = ai_matching_engine.find_matches_for_project(project_id)

        end_time = datetime.datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000

        return jsonify({
            'success': True,
            'matches': matches,
            'total_matches': len(matches),
            'processing_time_ms': round(processing_time, 2)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to find matches: {str(e)}'}), 500
