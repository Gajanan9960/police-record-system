from flask import Blueprint

malkhana = Blueprint('malkhana', __name__)

from app.malkhana import routes
