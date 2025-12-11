from flask import redirect, url_for
from flask_login import current_user
from app.main import main

@main.route('/')
@main.route('/home')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('dashboard.admin_dashboard'))
        elif current_user.role == 'officer' or current_user.role == 'io':
            return redirect(url_for('dashboard.officer_dashboard'))
        elif current_user.role == 'sho':
            return redirect(url_for('sho.dashboard'))
        elif current_user.role == 'clerk':
            return redirect(url_for('clerk.register_fir'))
        # Add other roles as needed
        return redirect(url_for('dashboard.officer_dashboard')) # Default fallback
    return redirect(url_for('auth.login'))
