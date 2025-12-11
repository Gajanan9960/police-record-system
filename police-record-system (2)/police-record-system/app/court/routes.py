from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.court import court
from app.models import Case
from app.utils import roles_required

@court.route('/dashboard')
@login_required
@roles_required('court')
def dashboard():
    # Cases that are ready for court or already in court
    # Assuming 'Court' status or specific flag
    # Let's say cases with status 'Court' or 'Closed' (verdict delivered)
    # Or maybe we need a way to send cases to court from IO/SHO?
    # For now, let's show all cases where status is 'Court'
    cases = Case.query.filter(Case.status == 'Court').all()
    return render_template('court/dashboard.html', cases=cases)

@court.route('/case/<int:case_id>/update', methods=['POST'])
@login_required
@roles_required('court')
def update_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    court_status = request.form.get('court_status')
    verdict = request.form.get('verdict')
    
    if court_status:
        case.court_status = court_status
    
    if verdict:
        case.verdict = verdict
        case.status = 'Closed' # Case closed after verdict?
        
    db.session.commit()
    flash('Court details updated.', 'success')
    
    return redirect(url_for('court.dashboard'))
