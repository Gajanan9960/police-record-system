from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.clerk import clerk
from app.models import FIR, Case
from app.utils import roles_required
from app.forms import FIRForm
from datetime import datetime

@clerk.route('/fir/register', methods=['GET', 'POST'])
@login_required
@roles_required('clerk')
def register_fir():
    form = FIRForm()
    if form.validate_on_submit():
        # Generate Sequential FIR Number
        now = datetime.now()
        year = now.strftime('%Y')
        fir_prefix = f"FIR-{year}-"
        fir_count = FIR.query.filter(FIR.fir_number.like(f"{fir_prefix}%")).count()
        fir_num = f"{fir_prefix}{str(fir_count + 1).zfill(3)}"
        
        # Generate Sequential Case Number (Match standard format)
        case_prefix = f"CASE-{year}-"
        case_count = Case.query.filter(Case.case_number.like(f"{case_prefix}%")).count()
        case_num = f"{case_prefix}{str(case_count + 1).zfill(4)}"
        
        # Create a Case first
        case = Case(
            case_number=case_num,
            title=f"FIR Case {fir_num}",
            description=form.details.data,
            status='Open',
            priority='Medium',
            created_by_id=current_user.id,
            location="Station", # Default or add to form
            station_id=current_user.station_id # Explicit station assign
        )
        db.session.add(case)
        db.session.commit()
        
        fir = FIR(
            fir_number=fir_num,
            case_id=case.id,
            filed_by_id=current_user.id,
            details=form.details.data,
            witnesses=form.witnesses.data,
            status='Pending',
            station_id=current_user.station_id # Explicit station assign
        )
        db.session.add(fir)
        db.session.commit()
        
        flash(f'FIR {fir_num} registered successfully.', 'success')
        return redirect(url_for('clerk.pending_firs'))
        
    return render_template('clerk/register_fir.html', form=form)

@clerk.route('/fir/pending')
@login_required
@roles_required('clerk')
def pending_firs():
    # Show all pending FIRs that haven't been forwarded yet? 
    # Or show all pending FIRs regardless?
    # Let's show all FIRs with status 'Pending'
    firs = FIR.query.filter_by(status='Pending').all()
    return render_template('clerk/pending_firs.html', firs=firs)

@clerk.route('/fir/<int:fir_id>/forward', methods=['POST'])
@login_required
@roles_required('clerk')
def forward_fir(fir_id):
    fir = FIR.query.get_or_404(fir_id)
    fir.forwarded_to_sho = True
    db.session.commit()
    flash(f'FIR {fir.fir_number} forwarded to SHO.', 'success')
    return redirect(url_for('clerk.pending_firs'))
