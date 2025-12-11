from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.malkhana import malkhana
from app.models import Evidence, User
from app.utils import roles_required
from datetime import datetime

@malkhana.route('/dashboard')
@login_required
@roles_required('malkhana')
def dashboard():
    # Show all evidence
    evidence_list = Evidence.query.all()
    return render_template('malkhana/dashboard.html', evidence_list=evidence_list)

@malkhana.route('/evidence/<int:evidence_id>/checkin', methods=['POST'])
@login_required
@roles_required('malkhana')
def checkin_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    location = request.form.get('location')
    
    if location:
        evidence.location = location
        evidence.status = 'In Custody'
        evidence.custodian_id = current_user.id
        db.session.commit()
        flash(f'Evidence {evidence.id} checked in at {location}.', 'success')
    
    return redirect(url_for('malkhana.dashboard'))

@malkhana.route('/evidence/<int:evidence_id>/checkout', methods=['POST'])
@login_required
@roles_required('malkhana')
def checkout_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    recipient_id = request.form.get('recipient_id') # User ID of IO/Forensic/Court
    reason = request.form.get('reason') # e.g., "Forensic Analysis", "Court Hearing"
    
    if recipient_id:
        evidence.status = f'Checked Out ({reason})'
        evidence.custodian_id = recipient_id
        db.session.commit()
        flash(f'Evidence {evidence.id} checked out.', 'success')
    
    return redirect(url_for('malkhana.dashboard'))
