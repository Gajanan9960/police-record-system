from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.tasks import tasks
from app.models import Task, Case, User
from app.utils import log_audit, station_scoped
from datetime import datetime

@tasks.route('/case/<int:case_id>/tasks/create', methods=['POST'])
@login_required
def create_task(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Permission: Only Admin, Inspector, or Assigned Officer/Team can create tasks
    is_authorized = (current_user.role in ['admin', 'inspector']) or \
                    (case.assigned_officer_id == current_user.id) or \
                    (current_user in case.officers)
                    
    if not is_authorized:
        flash('You are not authorized to assign tasks for this case.', 'danger')
        return redirect(url_for('cases.case_detail', case_id=case_id))

    title = request.form.get('task_title')
    description = request.form.get('task_description')
    assigned_to_id = request.form.get('assigned_to_id')
    priority = request.form.get('priority')
    due_date_str = request.form.get('due_date')
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass            

    task = Task(
        case_id=case.id,
        station_id=current_user.station_id,
        title=title,
        description=description,
        assigned_to_id=assigned_to_id,
        assigned_by_id=current_user.id,
        priority=priority,
        due_date=due_date,
        status='Pending'
    )
    
    db.session.add(task)
    db.session.commit()
    
    assignee = User.query.get(assigned_to_id)
    log_audit('CREATE', 'Task', task.id, f"Task '{title}' assigned to {assignee.full_name}")
    flash('Task assigned successfully.', 'success')
    
    return redirect(url_for('cases.case_detail', case_id=case_id))

@tasks.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Permission: Only Assignee, Assigner, Admin, Inspector
    is_authorized = (current_user.id == task.assigned_to_id) or \
                    (current_user.id == task.assigned_by_id) or \
                    (current_user.role in ['admin', 'inspector'])
                    
    if not is_authorized:
        flash('Unauthorized to update this task.', 'danger')
        return redirect(request.referrer or url_for('dashboard.officer_dashboard'))
        
    new_status = request.form.get('status')
    if new_status:
        task.status = new_status
        if new_status == 'Completed':
            task.completed_at = datetime.utcnow()
            
        db.session.commit()
        log_audit('UPDATE', 'Task', task.id, f"Task status updated to {new_status}")
        flash(f'Task marked as {new_status}.', 'success')
        
    return redirect(request.referrer or url_for('dashboard.officer_dashboard'))
