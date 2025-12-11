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
    
    query = Case.query
    
    if search_query:
        transliterated_query = transliterate_to_english(search_query)
        search_terms = {search_query, transliterated_query}
        conditions = []
        for term in search_terms:
            like_pattern = f"%{term}%"
            conditions.extend([
                Case.case_number.ilike(like_pattern),
                Case.title.ilike(like_pattern),
                Case.description.ilike(like_pattern)
            ])
        query = query.filter(or_(*conditions))
        
    cases_list = query.order_by(Case.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('cases.html', cases=cases_list, search_query=search_query)

from app.models import Case, FIR, User, Participant, Evidence, case_officers
from app.utils import transliterate_to_english, station_scoped, log_audit
from sqlalchemy import or_
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure upload folder (ensure this path exists)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'evidence')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@cases.route('/cases/new', methods=['GET', 'POST'])
@login_required
def create_case():
    form = CaseForm()
    
    # Populate Inspector/Officer Choices (Station Scoped)
    inspectors = station_scoped(User.query).filter_by(role='inspector').all()
    officers = station_scoped(User.query).filter_by(role='officer').all()
    
    form.assigned_officer_id.choices = [(u.id, u.full_name) for u in inspectors]
    form.officer_ids.choices = [(u.id, u.full_name) for u in officers] 
    
    if form.validate_on_submit():
        # Auto-generate Case Number if empty (Simple logic for now)
        case_num = form.case_number.data
        if not case_num:
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            case_num = f"CASE-{current_user.station_id}-{timestamp}"

        case = Case(
            station_id=current_user.station_id,
            case_number=case_num,
            title=form.title.data,
            offense_type=form.offense_type.data,
            short_description=form.short_description.data,
            description=form.description.data,
            incident_date=form.incident_date.data,
            location=form.location.data,
            gps_coordinates=form.gps_coordinates.data,
            status=form.status.data,
            priority=form.priority.data,
            confidentiality_level=form.confidentiality_level.data,
            tags=form.tags.data,
            related_case_ids=form.related_case_ids.data,
            
            is_cognizable=form.is_cognizable.data,
            ipc_sections=form.ipc_sections.data,
            init_medical_exam=form.init_medical_exam.data,
            init_prelim_enquiry=form.init_prelim_enquiry.data,
            init_scene_visit=form.init_scene_visit.data,
            created_by_id=current_user.id,
            assigned_officer_id=form.assigned_officer_id.data
        )
        
        db.session.add(case)
        db.session.flush() # Get ID
        
        # Handle Participants (Dynamic List from Form Request - Manual Parsing)
        # Expecting inputs like participant_name[], participant_type[], etc.
        names = request.form.getlist('participant_name[]')
        types = request.form.getlist('participant_type[]')
        contacts = request.form.getlist('participant_contact[]')
        details = request.form.getlist('participant_details[]')
        dobs = request.form.getlist('participant_dob[]')
        national_ids = request.form.getlist('participant_national_id[]')
        addresses = request.form.getlist('participant_address[]')
        
        for i in range(len(names)):
            if names[i]:
                # Basic server-side validation for name length
                if len(names[i]) < 2 or len(names[i]) > 100:
                    continue 

                p = Participant(
                    case_id=case.id,
                    name=names[i],
                    type=types[i] if i < len(types) else 'Witness',
                    contact_info=contacts[i] if i < len(contacts) else '',
                    details=details[i] if i < len(details) else '',
                    dob=datetime.strptime(dobs[i], '%Y-%m-%d').date() if i < len(dobs) and dobs[i] else None,
                    national_id=national_ids[i] if i < len(national_ids) else None,
                    address=addresses[i] if i < len(addresses) else None
                )
                db.session.add(p)
        
        # Handle Team Assignment (Officers)
        selected_officer_ids = request.form.getlist('officer_ids') # Multi-select
        for officer_id in selected_officer_ids:
            officer = User.query.get(int(officer_id))
            if officer and officer.station_id == current_user.station_id:
                case.officers.append(officer)
        
        # Handle Evidence Uploads
        if form.evidence_files.data:
            for file in form.evidence_files.data:
                if file.filename:
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to avoid collisions
                    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(filepath)
                    
                    evidence = Evidence(
                        station_id=current_user.station_id,
                        case_id=case.id,
                        description=form.evidence_description.data or f"Uploaded file: {filename}",
                        type="Digital",
                        location=unique_filename, # Storing relative filename
                        custodian_id=current_user.id
                    )
                    db.session.add(evidence)

        db.session.commit()
        log_audit('CREATE', 'Case', case.id, f"Created case {case.case_number}")
        flash('Case created successfully!', 'success')
        return redirect(url_for('cases.case_detail', case_id=case.id))
        
    return render_template('create_case.html', title='New Case', form=form)

@cases.route('/cases/<int:case_id>')
@login_required
def case_detail(case_id):
    case = Case.query.get_or_404(case_id)
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
