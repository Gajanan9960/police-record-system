from flask import Blueprint

forensic = Blueprint('forensic', __name__)

from app.forensic import routes
