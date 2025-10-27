from flask import jsonify
from . import main
import datetime

@main.route('/api/v1/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API is running
    """
    return jsonify({
        'status': 'healthy',
        'service': 'NeuraSynth Studios API',
        'version': '2.0.0',
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

@main.app_errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@main.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500
