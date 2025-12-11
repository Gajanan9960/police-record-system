from flask import Blueprint

io = Blueprint('io', __name__)

from app.io import routes
