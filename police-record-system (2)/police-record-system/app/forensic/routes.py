from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.forensic import forensic
from app.models import Evidence
from app.utils import roles_required

@forensic.route('/dashboard')
@login_required
@roles_required('forensic')
def dashboard():
    # Show evidence assigned to current forensic user or checked out for analysis
    # Assuming 'custodian_id' points to the forensic user when checked out
    my_tasks = Evidence.query.filter_by(custodian_id=current_user.id).all()
    return render_template('forensic/dashboard.html', tasks=my_tasks)

@forensic.route('/evidence/<int:evidence_id>/upload_report', methods=['POST'])
@login_required
@roles_required('forensic')
def upload_report(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    
    if evidence.custodian_id != current_user.id:
        flash('You are not the custodian of this evidence.', 'danger')
        return redirect(url_for('forensic.dashboard'))
        
    report_text = request.form.get('report_text')
    
    if report_text:
        # In a real app, we might upload a file. Here we append to description or status
        evidence.description += f" [Forensic Report: {report_text}]"
        evidence.status = 'Analysis Complete'
        db.session.commit()
        flash('Forensic report uploaded.', 'success')
        
    return redirect(url_for('forensic.dashboard'))
