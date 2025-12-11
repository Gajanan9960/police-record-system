from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.io import io
from app.models import Case, Evidence, Statement, InvestigationUpdate
from app.utils import roles_required
from datetime import datetime

@io.route('/dashboard')
@login_required
@roles_required('io')
def dashboard():
    # Cases assigned to the current IO
    my_cases = Case.query.filter_by(assigned_officer_id=current_user.id).all()
    return render_template('io/dashboard.html', cases=my_cases)

@io.route('/case/<int:case_id>/investigate', methods=['GET', 'POST'])
@login_required
@roles_required('io')
def investigate_case(case_id):
    case = Case.query.get_or_404(case_id)
    if case.assigned_officer_id != current_user.id:
        flash('You are not assigned to this case.', 'danger')
        return redirect(url_for('io.dashboard'))
        
    if request.method == 'POST':
        # Add Investigation Update
        update_text = request.form.get('update_text')
        if update_text:
            update = InvestigationUpdate(
                case_id=case.id,
                officer_id=current_user.id,
                description=update_text
            )
            db.session.add(update)
            db.session.commit()
            flash('Investigation update added.', 'success')
            return redirect(url_for('io.investigate_case', case_id=case.id))
            
    return render_template('io/investigate.html', case=case)

@io.route('/case/<int:case_id>/add_evidence', methods=['POST'])
@login_required
@roles_required('io')
def add_evidence(case_id):
    case = Case.query.get_or_404(case_id)
    if case.assigned_officer_id != current_user.id:
        return redirect(url_for('io.dashboard'))
        
    description = request.form.get('description')
    type = request.form.get('type')
    location = request.form.get('location')
    
    if description:
        evidence = Evidence(
            case_id=case.id,
            description=description,
            type=type,
            location=location,
            custodian_id=current_user.id, # Initially with IO
            status='In Custody'
        )
        db.session.add(evidence)
        db.session.commit()
        flash('Evidence added.', 'success')
        
    return redirect(url_for('io.investigate_case', case_id=case.id))

@io.route('/case/<int:case_id>/add_statement', methods=['POST'])
@login_required
@roles_required('io')
def add_statement(case_id):
    case = Case.query.get_or_404(case_id)
    if case.assigned_officer_id != current_user.id:
        return redirect(url_for('io.dashboard'))
        
    person_name = request.form.get('person_name')
    type = request.form.get('type')
    content = request.form.get('content')
    
    if person_name and content:
        statement = Statement(
            case_id=case.id,
            recorded_by_id=current_user.id,
            person_name=person_name,
            type=type,
            content=content
        )
        db.session.add(statement)
        db.session.commit()
        flash('Statement recorded.', 'success')
        
    return redirect(url_for('io.investigate_case', case_id=case.id))
