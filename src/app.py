from flask import Flask
import json
from flask_cors import CORS
from .config import config
from datetime import date

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return json.JSONEncoder.default(self, obj)

def create_app(config_name='default'):
    """
    Creates and configures a Flask application instance.
    """
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder

    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    from .models import db
    db.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))

    # Register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/v1/auth')

    from .users import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/api/v1/users')

    from .projects import projects as projects_blueprint
    app.register_blueprint(projects_blueprint, url_prefix='/api/v1/projects')

    from .contributors import contributors as contributors_blueprint
    app.register_blueprint(contributors_blueprint, url_prefix='/api/v1/contributors')

    from .automation_blueprint import automation_bp
    app.register_blueprint(automation_bp, url_prefix='/api/v1/automation')

    from .financial_blueprint import financial_bp
    app.register_blueprint(financial_bp, url_prefix='/api/v1/financial')

    return app
