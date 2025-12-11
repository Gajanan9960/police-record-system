from flask import request, render_template
from flask_login import current_user
from app import db, login_manager
from functools import wraps
from app.models import AuditLog
from datetime import datetime

def transliterate_to_english(text):
    """
    Placeholder for transliteration logic.
    Returns the text as is for now.
    """
    return text

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in roles and current_user.role != 'admin':
                return render_template('403.html'), 403
            return f(*args, **kwargs)
        return decorated_view
    return wrapper

def log_audit(action, object_type=None, object_id=None, details=None):
    """
    Logs an action to the AuditLog table.
    """
    if not current_user.is_authenticated:
        return

    log = AuditLog(
        station_id=current_user.station_id,
        user_id=current_user.id,
        action=action,
        object_type=object_type,
        object_id=object_id,
        details=details,
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

def station_scoped(query):
    """
    Filters a query to the current user's station.
    Usage: station_scoped(Case.query).all()
    """
    if not current_user.is_authenticated:
        return query.filter(False) # No access if not logged in
    
    # Assuming the model has 'station_id'
    return query.filter_by(station_id=current_user.station_id)
