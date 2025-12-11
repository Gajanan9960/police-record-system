from flask import Blueprint

criminals = Blueprint('criminals', __name__)

from app.criminals import routes
