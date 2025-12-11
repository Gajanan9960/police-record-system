from flask import Blueprint

cases = Blueprint('cases', __name__)

from app.cases import routes
