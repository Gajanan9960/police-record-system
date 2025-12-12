from flask import render_template
from flask_login import login_required
from app.forensic import forensic
from app.models import Evidence
from app.utils import roles_required

@forensic.route('/forensic/dashboard')
@login_required
@roles_required('forensic')
def dashboard():
    # Show evidence needing analysis
    evidence = Evidence.query.all()
    return render_template('forensic_dashboard.html', evidence=evidence)
