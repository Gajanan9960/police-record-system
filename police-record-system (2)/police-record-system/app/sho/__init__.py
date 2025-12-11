from flask import Blueprint

sho = Blueprint('sho', __name__)

from app.sho import routes
