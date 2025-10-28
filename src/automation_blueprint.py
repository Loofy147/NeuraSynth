# -*- coding: utf-8 -*-
"""
Blueprint for automation management endpoints.
"""

from flask import Blueprint, jsonify, request
from .intelligent_automation import IntelligentAutomationEngine, ProjectHealthMonitor
from .models import db

automation_bp = Blueprint('automation_bp', __name__)
automation_engine = IntelligentAutomationEngine(db)
health_monitor = ProjectHealthMonitor(db, automation_engine)

@automation_bp.route('/rules', methods=['POST'])
def add_automation_rule():
    """Add a new automation rule."""
    rule_data = request.get_json()
    if not rule_data:
        return jsonify({"error": "Invalid input"}), 400

    success = automation_engine.add_automation_rule(rule_data)
    if success:
        return jsonify({"message": "Automation rule added successfully"}), 201
    else:
        return jsonify({"error": "Failed to add automation rule"}), 500

@automation_bp.route('/rules/<rule_id>', methods=['DELETE'])
def remove_automation_rule(rule_id):
    """Remove an automation rule."""
    success = automation_engine.remove_automation_rule(rule_id)
    if success:
        return jsonify({"message": "Automation rule removed successfully"}), 200
    else:
        return jsonify({"error": "Failed to remove automation rule"}), 500

@automation_bp.route('/stats', methods=['GET'])
def get_automation_stats():
    """Get automation engine statistics."""
    stats = automation_engine.get_automation_statistics()
    return jsonify(stats), 200

@automation_bp.route('/projects/<project_id>/monitor', methods=['POST'])
def monitor_project_health(project_id):
    """Analyze and report project health."""
    health_analysis = health_monitor.monitor_project(project_id)
    if health_analysis:
        return jsonify(health_analysis), 200
    else:
        return jsonify({"error": "Failed to analyze project health"}), 500
