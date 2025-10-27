from flask import Blueprint

contributors = Blueprint('contributors', __name__)

from . import routes
