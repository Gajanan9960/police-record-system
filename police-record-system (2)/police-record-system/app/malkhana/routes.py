from flask import render_template
from flask_login import login_required
from app.malkhana import malkhana
from app.models import Evidence
from app.utils import roles_required

@malkhana.route('/malkhana/dashboard')
@login_required
@roles_required('malkhana')
def dashboard():
    # Show evidence in custody
    evidence = Evidence.query.all()
    return render_template('malkhana_dashboard.html', evidence=evidence)
