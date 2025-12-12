from flask import render_template
from flask_login import login_required
from app.court import court
from app.models import Case
from app.utils import roles_required

@court.route('/court/dashboard')
@login_required
@roles_required('court')
def dashboard():
    cases = Case.query.filter_by(status='Court').all()
    return render_template('court_dashboard.html', cases=cases)
