from flask import render_template
from flask_login import login_required, current_user
from app.dashboard import dashboard
from app.models import Case, User, FIR

from app.utils import station_scoped

@dashboard.route('/dashboard/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return render_template('403.html'), 403
    
    # Key Metrics (Station Scoped)
    total_cases = station_scoped(Case.query).count()
    total_users = station_scoped(User.query).count()
    closed_cases = station_scoped(Case.query).filter_by(status='Closed').count()
    pending_firs = station_scoped(FIR.query).filter_by(status='Pending').count()
    
    # Solved Rate
    solved_rate = round((closed_cases / total_cases * 100), 1) if total_cases > 0 else 0
    
    # Recent Activity (Latest 5 cases)
    recent_cases = station_scoped(Case.query).order_by(Case.created_at.desc()).limit(5).all()
    
    # Case Status Distribution
    status_counts = {
        'Open': station_scoped(Case.query).filter_by(status='Open').count(),
        'In Progress': station_scoped(Case.query).filter_by(status='In Progress').count(),
        'Closed': closed_cases,
        'Court': station_scoped(Case.query).filter_by(status='Court').count(),
        'Pending': station_scoped(Case.query).filter_by(status='Pending').count()
    }
    
    # SHO Tasks (Merged for Admin)
    pending_firs_list = station_scoped(FIR.query).filter_by(status='Pending', forwarded_to_sho=True).all()
    active_cases = station_scoped(Case.query).filter(Case.status.in_(['Open', 'In Progress', 'Pending'])).all()
    assignable_officers = station_scoped(User.query).filter(User.role.in_(['io', 'officer'])).all()
    
    return render_template('admin_dashboard.html', 
                           total_cases=total_cases, 
                           total_users=total_users,
                           closed_cases=closed_cases,
                           pending_firs=pending_firs,
                           solved_rate=solved_rate,
                           recent_cases=recent_cases,
                           status_counts=status_counts,
                           pending_firs_list=pending_firs_list,
                           active_cases=active_cases,
                           ios=assignable_officers)

@dashboard.route('/dashboard/officer')
@login_required
def officer_dashboard():
    # Officer sees only assigned cases
    my_cases = Case.query.filter_by(assigned_officer_id=current_user.id).all()
    return render_template('officer_dashboard.html', cases=my_cases)

@dashboard.route('/dashboard/inspector')
@login_required
def inspector_dashboard():
    # Inspector sees all cases in station + SHO capabilities (Approvals/Assignments)
    all_cases = station_scoped(Case.query).all()
    
    # SHO Tasks (Merged for Inspector)
    pending_firs_list = station_scoped(FIR.query).filter_by(status='Pending', forwarded_to_sho=True).all()
    active_cases = station_scoped(Case.query).filter(Case.status.in_(['Open', 'In Progress'])).all()
    
    # Fetch IOs and Officers for assignment
    assignable_officers = station_scoped(User.query).filter(User.role.in_(['io', 'officer'])).all()
    
    return render_template('inspector_dashboard.html', 
                           cases=all_cases,
                           pending_firs_list=pending_firs_list,
                           active_cases=active_cases,
                           ios=assignable_officers)
