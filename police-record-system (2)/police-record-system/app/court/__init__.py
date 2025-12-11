from flask import Blueprint

court = Blueprint('court', __name__)

from app.court import routes
