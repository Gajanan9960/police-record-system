from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.cases import cases
from app.forms import CaseForm, FIRForm
from app.models import Case, FIR, User, Participant, Evidence, case_officers
from app.utils import transliterate_to_english
from sqlalchemy import or_

@cases.route('/cases')
@login_required
def list_cases():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    
    # Base query: Scoped to station
    query = station_scoped(Case.query)
    
    # Strict Isolation Logic
    if current_user.role in ['admin', 'inspector']:
        pass # Admin/Inspector see all cases in station
    elif current_user.role in ['officer', 'io']:
        # Officers/IOs see assigned cases only
        query = query.filter(or_(
            Case.assigned_officer_id == current_user.id,
            Case.officers.any(id=current_user.id)
        ))
    else:
        # Others (Clerk, etc.) see only cases they created
        query = query.filter(Case.created_by_id == current_user.id)
    
    if search_query:
        transliterated_query = transliterate_to_english(search_query)
# ... lines 27-40 ...
@cases.route('/cases/<int:case_id>')
@login_required
def case_detail(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Enforce Isolation
    if current_user.role in ['officer', 'io']:
        is_assigned = (case.assigned_officer_id == current_user.id)
        is_team_member = (current_user in case.officers)
        if not (is_assigned or is_team_member):
             flash('You do not have permission to view this case.', 'danger')
             return redirect(url_for('cases.list_cases'))

    return render_template('case_detail.html', case=case)

@cases.route('/cases/<int:case_id>/add_fir', methods=['GET', 'POST'])
@login_required
def add_fir(case_id):
    case = Case.query.get_or_404(case_id)
    form = FIRForm()
    if form.validate_on_submit():
        fir = FIR(fir_number=form.fir_number.data, details=form.details.data,
                  witnesses=form.witnesses.data, case_id=case.id, filed_by_id=current_user.id)
        db.session.add(fir)
        db.session.commit()
        flash('FIR filed successfully!', 'success')
        return redirect(url_for('cases.case_detail', case_id=case.id))
    return render_template('add_fir.html', title='File FIR', form=form, case=case)

from flask import jsonify
@cases.route('/cases/next-id')
@login_required
def get_next_case_id():
    now = datetime.now()
    year = now.strftime('%Y')
    prefix = f"CASE-{year}-"
    count = Case.query.filter(Case.case_number.like(f"{prefix}%")).count()
    sequence = str(count + 1).zfill(4)
    return jsonify({'next_id': f"{prefix}{sequence}"})

@cases.route('/cases/<int:case_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Permission Check
    # Inspector can edit any case in station. Officer can edit if assigned.
    if current_user.role == 'officer':
        if case.assigned_officer_id != current_user.id and current_user not in case.officers:
             flash('You do not have permission to edit this case.', 'danger')
             return redirect(url_for('cases.case_detail', case_id=case_id))
    
    form = CaseForm(obj=case)
    
    # Scope choices
    inspectors = station_scoped(User.query).filter_by(role='inspector').all()
    officers = station_scoped(User.query).filter_by(role='officer').all()
    form.assigned_officer_id.choices = [(u.id, u.full_name) for u in inspectors]
    form.officer_ids.choices = [(u.id, u.full_name) for u in officers]

    if form.validate_on_submit():
        form.populate_obj(case)
        # Manually update M2M and Custom Fields
        
        # Officers team
        selected_officer_ids = request.form.getlist('officer_ids')
        case.officers = [] # Reset and re-add
        for officer_id in selected_officer_ids:
             officer = User.query.get(int(officer_id))
             if officer:
                 case.officers.append(officer)
        
        # Participants Handling
        p_ids = request.form.getlist('participant_id[]')
        names = request.form.getlist('participant_name[]')
        types = request.form.getlist('participant_type[]')
        contacts = request.form.getlist('participant_contact[]')
        # ... fetch other lists ...
        details = request.form.getlist('participant_details[]')
        dobs = request.form.getlist('participant_dob[]')
        national_ids = request.form.getlist('participant_national_id[]')
        addresses = request.form.getlist('participant_address[]')

        # Current IDs in DB
        current_p_ids = [p.id for p in case.participants]
        submitted_p_ids = [int(pid) for pid in p_ids if pid != 'new']
        
        # Delete removed
        for pid in current_p_ids:
            if pid not in submitted_p_ids:
                Participant.query.filter_by(id=pid).delete()
        
        # Add/Update
        for i in range(len(names)):
            if not names[i]: continue
            
            pid = p_ids[i]
            if pid == 'new':
                 p = Participant(case_id=case.id)
                 db.session.add(p)
            else:
                 p = Participant.query.get(int(pid))
            
            if p:
                p.name = names[i]
                p.type = types[i] if i < len(types) else 'Witness'
                p.contact_info = contacts[i] if i < len(contacts) else ''
                p.details = details[i] if i < len(details) else ''
                p.dob = datetime.strptime(dobs[i], '%Y-%m-%d').date() if i < len(dobs) and dobs[i] else None
                p.national_id = national_ids[i] if i < len(national_ids) else None
                p.address = addresses[i] if i < len(addresses) else None

        # Evidence (Append New)
        if form.evidence_files.data:
             for file in form.evidence_files.data:
                if file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(filepath)
                    
                    evidence = Evidence(
                        station_id=current_user.station_id,
                        case_id=case.id,
                        description=form.evidence_description.data or f"Uploaded file: {filename}",
                        type="Digital",
                        location=unique_filename,
                        custodian_id=current_user.id,
                        collected_at=form.evidence_collected_at.data or datetime.utcnow()
                    )
                    db.session.add(evidence)

        db.session.commit()
        log_audit('UPDATE', 'Case', case.id, f"Updated case {case.case_number}")
        flash('Case updated successfully.', 'success')
        return redirect(url_for('cases.case_detail', case_id=case.id))

    # Pre-select M2M
    form.officer_ids.data = [o.id for o in case.officers]
    return render_template('edit_case.html', form=form, case=case)
