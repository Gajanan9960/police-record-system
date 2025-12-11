from flask import Blueprint

clerk = Blueprint('clerk', __name__)

from app.clerk import routes
