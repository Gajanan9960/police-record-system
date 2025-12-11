from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.sho import sho
from app.models import FIR, Case, User
from app.utils import roles_required
from datetime import datetime

@sho.route('/dashboard')
@login_required
@roles_required('sho')
def dashboard():
    # Pending FIRs (forwarded by clerk)
    pending_firs = FIR.query.filter_by(status='Pending', forwarded_to_sho=True).all()
    
    # Active Cases (Open or In Progress)
    active_cases = Case.query.filter(Case.status.in_(['Open', 'In Progress'])).all()
    
    # List of IOs for assignment
    ios = User.query.filter_by(role='io').all()
    
    return render_template('sho/dashboard.html', pending_firs=pending_firs, active_cases=active_cases, ios=ios)

@sho.route('/fir/<int:fir_id>/approve', methods=['POST'])
@login_required
@roles_required('sho', 'inspector')
def approve_fir(fir_id):
    fir = FIR.query.get_or_404(fir_id)
    fir.status = 'Approved'
    fir.approved_by_id = current_user.id
    
    # Ensure Case status is Open (if it was Pending)
    if fir.case.status == 'Pending':
        fir.case.status = 'Open'
        
    db.session.commit()
    flash(f'FIR {fir.fir_number} approved.', 'success')
    
    if current_user.role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    elif current_user.role == 'inspector':
        return redirect(url_for('dashboard.inspector_dashboard'))
    return redirect(url_for('sho.dashboard'))

@sho.route('/fir/<int:fir_id>/reject', methods=['POST'])
@login_required
@roles_required('sho', 'inspector')
def reject_fir(fir_id):
    fir = FIR.query.get_or_404(fir_id)
    fir.status = 'Rejected'
    fir.approved_by_id = current_user.id
    db.session.commit()
    flash(f'FIR {fir.fir_number} rejected.', 'danger')
    
    if current_user.role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    elif current_user.role == 'inspector':
        return redirect(url_for('dashboard.inspector_dashboard'))
    return redirect(url_for('sho.dashboard'))

@sho.route('/case/<int:case_id>/assign', methods=['POST'])
@login_required
@roles_required('sho', 'inspector')
def assign_io(case_id):
    case = Case.query.get_or_404(case_id)
    io_id = request.form.get('io_id')
    
    if io_id:
        case.assigned_officer_id = io_id
        case.status = 'In Progress'
        db.session.commit()
        flash(f'Case {case.case_number} assigned to IO.', 'success')
    else:
        flash('Please select an IO.', 'warning')
        
    if current_user.role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    elif current_user.role == 'inspector':
        return redirect(url_for('dashboard.inspector_dashboard'))
    return redirect(url_for('sho.dashboard'))
