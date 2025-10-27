from flask import jsonify
from . import contributors
from ..contributors_hub import ContributorsHub
from ..utils import token_required

contributors_hub = ContributorsHub()

@contributors.route('/equity/<contributor_id>', methods=['GET'])
@token_required
def get_contributor_equity(current_user_id, contributor_id):
    """
    Get contributor equity information
    """
    try:
        # Check if user can access this equity information
        if current_user_id != contributor_id:
            pass

        equity_data = contributors_hub.get_equity_holdings(contributor_id)

        return jsonify({
            'success': True,
            'equity': equity_data
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get equity data: {str(e)}'}), 500

@contributors.route('/performance/<contributor_id>', methods=['GET'])
@token_required
def get_contributor_performance(current_user_id, contributor_id):
    """
    Get contributor performance metrics
    """
    try:
        performance_data = contributors_hub.get_performance_metrics(contributor_id)

        return jsonify({
            'success': True,
            'performance': performance_data
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get performance data: {str(e)}'}), 500
