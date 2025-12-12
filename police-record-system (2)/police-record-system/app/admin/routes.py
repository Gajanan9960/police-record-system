from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.admin import admin
from app.models import User, Station, AuditLog
from app.utils import log_audit
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return render_template('403.html'), 403
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin')
@login_required
@admin_required
def index():
    return redirect(url_for('dashboard.admin_dashboard'))

@admin.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.filter_by(station_id=current_user.station_id).all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    # Placeholder for user creation logic
    # Will implement form processing here
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        inspector_id = request.form.get('inspector_id')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.create_user'))
            
        user = User(
            username=username,
            email=email,
            role=role,
            full_name=full_name,
            station_id=current_user.station_id
        )
        user.set_password(password)
        
        if role == 'officer' and inspector_id:
            user.inspector_id = int(inspector_id)
            
        db.session.add(user)
        db.session.commit()
        log_audit('CREATE', 'User', user.id, f"Created user {user.username} as {role}")
        flash('User created successfully', 'success')
        return redirect(url_for('admin.users'))

    inspectors = User.query.filter_by(station_id=current_user.station_id, role='inspector').all()
    return render_template('admin/create_user.html', inspectors=inspectors)

@admin.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.station_id != current_user.station_id:
        return render_template('403.html'), 403
        
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'warning')
        return redirect(url_for('admin.users'))
        
    db.session.delete(user)
    db.session.commit()
    log_audit('DELETE', 'User', user.id, f"Deleted user {user.username}")
    flash(f'User {user.username} deleted successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    station = Station.query.get(current_user.station_id)
    if request.method == 'POST':
        station.name = request.form.get('name')
        station.address = request.form.get('address')
        station.contact_info = request.form.get('contact_info')
        station.fir_prefix_format = request.form.get('fir_prefix_format')
        
        db.session.commit()
        log_audit('UPDATE', 'Station', station.id, "Updated station settings")
        flash('Settings updated', 'success')
        return redirect(url_for('admin.settings'))
        
    return render_template('admin/settings.html', station=station)

@admin.route('/admin/audit')
@login_required
@admin_required
def audit_logs():
    logs = AuditLog.query.filter_by(station_id=current_user.station_id).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/audit.html', logs=logs)
