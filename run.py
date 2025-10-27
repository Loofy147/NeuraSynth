import os
from src.app import create_app
from src.models import db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
