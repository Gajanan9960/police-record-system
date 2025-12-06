import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from sqlalchemy import or_
from sqlalchemy.sql import func
import re
from rapidfuzz import fuzz
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, HK, DEVANAGARI

def transliterate_to_english(text):
    """
    Detects if text contains Devanagari and transliterates to English (HK scheme).
    Returns the transliterated text or original if no Devanagari found.
    """
    # Simple check for Devanagari range (U+0900 to U+097F)
    if any('\u0900' <= char <= '\u097f' for char in text):
        try:
            # Transliterate from Devanagari to Harvard-Kyoto (HK) which maps well to English
            # We could also use ITRANS but HK is often simpler for direct mapping
            return sanscript.transliterate(text, sanscript.DEVANAGARI, sanscript.HK)
        except Exception as e:
            print(f"Transliteration error: {e}")
            return text
    return text

from functools import wraps
from flask import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///police.db'

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sahil.sahu.root@gmail.com'  # REPLACE THIS
app.config['MAIL_PASSWORD'] = 'ceba inqz zone frdm'     # REPLACE THIS

mail = Mail(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Constants
CASE_TYPES = {
    "Theft": "IPC 378",
    "Burglary": "IPC 445",
    "Assault": "IPC 351",
    "Fraud": "IPC 420",
    "Cyber Crime": "IT Act 66",
    "Drug Offense": "NDPS Act",
    "Traffic Violation": "MV Act",
    "Homicide": "IPC 300",
    "Kidnapping": "IPC 359"
}

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, officer, inspector, constable
    full_name = db.Column(db.String(120), nullable=False)
    badge_number = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_active

    def get_id(self):
        return str(self.id)


class PoliceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    suspect_name = db.Column(db.String(120), nullable=False)
    suspect_age = db.Column(db.Integer)
    victim_name = db.Column(db.String(120))
    victim_contact = db.Column(db.String(20))
    location = db.Column(db.String(200), nullable=False)
    incident_date = db.Column(db.DateTime, nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, approved, closed
    severity = db.Column(db.String(50))  # low, medium, high
    evidence = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    officer = db.relationship('User', backref='records')


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')  # open, in_progress, closed, pending_approval, rejected
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    lead_officer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead_officer = db.relationship('User', foreign_keys=[lead_officer_id], backref='lead_cases')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    incidents = db.relationship('CaseIncident', backref='case', cascade='all, delete-orphan')
    evidence_items = db.relationship('CaseEvidence', backref='case', cascade='all, delete-orphan')
    firs = db.relationship('FirstInformationReport', backref='case', cascade='all, delete-orphan')
    assignments = db.relationship('CaseAssignment', backref='case', cascade='all, delete-orphan')


class CaseIncident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    incident_type = db.Column(db.String(100))
    summary = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    incident_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_by = db.relationship('User', foreign_keys=[created_by_id])


class CaseEvidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    incident_id = db.Column(db.Integer, db.ForeignKey('case_incident.id'))
    description = db.Column(db.Text, nullable=False)
    storage_link = db.Column(db.String(255))
    file_name = db.Column(db.String(120))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    verified_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('CaseIncident')
    uploaded_by = db.relationship('User', foreign_keys=[uploaded_by_id])
    verified_by = db.relationship('User', foreign_keys=[verified_by_id])


class CustodyEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('case_evidence.id'), nullable=False)
    from_person = db.Column(db.String(120))
    to_person = db.Column(db.String(120), nullable=False)
    method = db.Column(db.String(120))
    notes = db.Column(db.Text)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    evidence = db.relationship('CaseEvidence', backref=db.backref('custody_events', cascade='all, delete-orphan'))
    recorded_by = db.relationship('User', foreign_keys=[recorded_by_id])


class FirstInformationReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    incident_id = db.Column(db.Integer, db.ForeignKey('case_incident.id'))
    fir_number = db.Column(db.String(50), unique=True, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    document_link = db.Column(db.String(255))
    filed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filed_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('CaseIncident')
    filed_by = db.relationship('User', foreign_keys=[filed_by_id])


class CaseAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50), default='support')  # lead, support, analyst
    status = db.Column(db.String(50), default='active')  # active, released
    notes = db.Column(db.Text)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    officer = db.relationship('User', foreign_keys=[officer_id], backref='case_assignments')


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))  # case, evidence, user, report
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='audit_logs')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def user_can_access_case(case, user):
    if user.role == 'admin':
        return True
    if user.role == 'inspector':
        # Inspectors can see all cases in their station (assuming single station for now)
        return True
    
    # Officers and Constables
    if case.lead_officer_id == user.id:
        return True
    
    return any(
        assignment.officer_id == user.id and assignment.status == 'active'
        for assignment in case.assignments
    )

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def inspector_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('admin', 'inspector'):
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def log_audit(action, target_type=None, target_id=None, details=None):
    try:
        log = AuditLog(
            user_id=current_user.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Failed to create audit log: {e}")
        db.session.rollback()



def normalize_text(value):
    return re.sub(r'\s+', ' ', value.strip().lower())


def score_record_for_search(record, term):
    normalized_term = normalize_text(term)
    term_tokens = set(normalized_term.split())
    candidates = [
        record.case_number,
        record.title,
        record.suspect_name,
        record.victim_name,
    ]
    best = 0
    for value in candidates:
        if not value:
            continue
        normalized_value = normalize_text(value)
        score = fuzz.token_sort_ratio(normalized_term, normalized_value)
        value_tokens = set(normalized_value.split())
        if term_tokens and term_tokens.issubset(value_tokens) and len(term_tokens) < len(value_tokens):
            score = min(score, 90)
        if score > best:
            best = score
    return best


def validate_record_form(form, record_id=None):
    errors = []
    cleaned = {}
    form_values = {}
    severity_options = {'low', 'medium', 'high'}
    
    # Date Validation (6 months rule)
    six_months_ago = datetime.utcnow() - datetime.timedelta(days=180)

    def get_value(name):
        value = (form.get(name) or '').strip()
        form_values[name] = value
        return value

    case_number = get_value('case_number')
    # If case_number is empty, we will auto-generate it later, so don't error here if it's missing
    # But if provided, check uniqueness
    if case_number:
        existing = PoliceRecord.query.filter_by(case_number=case_number)
        if record_id:
            existing = existing.filter(PoliceRecord.id != record_id)
        if existing.first():
            errors.append('Case number must be unique.')
    cleaned['case_number'] = case_number

    title = get_value('title')
    if len(title) < 5:
        errors.append('Title must be at least 5 characters.')
    cleaned['title'] = title

    description = get_value('description')
    if len(description) < 20:
        errors.append('Description must be at least 20 characters.')
    cleaned['description'] = description

    suspect_name = get_value('suspect_name')
    if not suspect_name:
        errors.append('Suspect name is required.')
    cleaned['suspect_name'] = suspect_name

    suspect_age_raw = get_value('suspect_age')
    if suspect_age_raw:
        try:
            suspect_age = int(suspect_age_raw)
            if suspect_age < 0 or suspect_age > 120:
                raise ValueError
            cleaned['suspect_age'] = suspect_age
        except ValueError:
            errors.append('Suspect age must be a number between 0 and 120.')
    else:
        cleaned['suspect_age'] = None

    victim_name = get_value('victim_name')
    cleaned['victim_name'] = victim_name or None

    victim_contact = get_value('victim_contact')
    if victim_contact:
        digits = re.sub(r'\D', '', victim_contact)
        if len(digits) != 10:
            errors.append('Victim contact must be exactly 10 digits.')
        elif not digits.isdigit():
            errors.append('Victim contact must contain only numbers.')
        cleaned['victim_contact'] = victim_contact
    else:
        cleaned['victim_contact'] = None

    location = get_value('location')
    if len(location) < 3:
        errors.append('Location is required.')
    cleaned['location'] = location

    incident_date_raw = get_value('incident_date')
    if not incident_date_raw:
        errors.append('Incident date and time is required.')
    else:
        try:
            # Try parsing ISO format first (from JS)
            incident_date = datetime.strptime(incident_date_raw, '%Y-%m-%dT%H:%M')
            
            if incident_date < six_months_ago:
                errors.append('Incident date cannot be older than 6 months.')
                
            cleaned['incident_date'] = incident_date
        except ValueError:
            errors.append('Invalid incident date format.')
    form_values['incident_date'] = incident_date_raw

    severity = get_value('severity').lower()
    if severity not in severity_options:
        errors.append('Severity must be low, medium, or high.')
    cleaned['severity'] = severity

    evidence = get_value('evidence')
    cleaned['evidence'] = evidence or None

    return cleaned, form_values, errors


# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('Incorrect current password', 'error')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'error')
        elif len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password updated successfully', 'success')
            return redirect(url_for('dashboard'))

    return render_template('change_password.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='recover-key')
            link = url_for('reset_password', token=token, _external=True)
            
            token = s.dumps(user.email, salt='recover-key')
            link = url_for('reset_password', token=token, _external=True)
            
            # Send email
            try:
                print(f"Attempting to send email to {user.email}...")
                msg = Message('Password Reset Request',
                            sender=app.config['MAIL_USERNAME'],
                            recipients=[user.email])
                msg.body = f'Your password reset link is: {link}\n\nIf you did not request this, please ignore this email.'
                mail.send(msg)
                print("Email sent successfully!")
                flash('If an account exists with that email, a reset link has been sent.', 'success')
            except Exception as e:
                print(f"Error sending email: {e}")
                import traceback
                traceback.print_exc()
                flash('Error sending email. Please try again later.', 'error')
            
            return redirect(url_for('login'))
        else:
            # Don't reveal if email exists or not for security
            flash('If an account exists with that email, a reset link has been sent.', 'success')
            return redirect(url_for('login'))

    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    try:
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = s.loads(token, salt='recover-key', max_age=3600) # 1 hour expiration
    except:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid user.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        else:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been updated! You can now login.', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'officer':
        return redirect(url_for('officer_dashboard'))
    elif current_user.role == 'inspector':
        return redirect(url_for('inspector_dashboard'))
    elif current_user.role == 'constable':
        return redirect(url_for('constable_dashboard'))
    return redirect(url_for('login'))


@app.route('/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    total_records = PoliceRecord.query.count()
    pending_records = PoliceRecord.query.filter_by(status='pending').count()
    total_users = User.query.count()
    total_cases = Case.query.count()
    open_cases = Case.query.filter_by(status='open').count()
    in_progress_cases = Case.query.filter_by(status='in_progress').count()
    closed_cases = Case.query.filter_by(status='closed').count()
    recent_cases = Case.query.order_by(Case.opened_at.desc()).limit(5).all()

    return render_template('admin_dashboard.html', users=users, total_records=total_records,
                         pending_records=pending_records, total_users=total_users,
                         total_cases=total_cases, open_cases=open_cases,
                         in_progress_cases=in_progress_cases, closed_cases=closed_cases,
                         recent_cases=recent_cases)


@app.route('/officer-dashboard')
@login_required
def officer_dashboard():
    if current_user.role != 'officer':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    my_records = PoliceRecord.query.filter_by(officer_id=current_user.id).all()
    pending = PoliceRecord.query.filter_by(officer_id=current_user.id, status='pending').count()
    approved = PoliceRecord.query.filter_by(officer_id=current_user.id, status='approved').count()
    case_query = Case.query.outerjoin(CaseAssignment).filter(
        or_(
            Case.lead_officer_id == current_user.id,
            CaseAssignment.officer_id == current_user.id
        )
    ).distinct()
    total_assigned_cases = case_query.count()
    open_assigned_cases = case_query.filter(Case.status != 'closed').count()
    closed_assigned_cases = case_query.filter(Case.status == 'closed').count()
    assigned_cases = case_query.order_by(Case.updated_at.desc()).limit(5).all()

    return render_template('officer_dashboard.html', records=my_records, pending=pending, approved=approved,
                           assigned_cases=assigned_cases, total_assigned_cases=total_assigned_cases,
                           open_assigned_cases=open_assigned_cases, closed_assigned_cases=closed_assigned_cases)


@app.route('/inspector-dashboard')
@login_required
@inspector_required
def inspector_dashboard():
    pending_records = PoliceRecord.query.filter_by(status='pending').all()
    approved_records = PoliceRecord.query.filter_by(status='approved').all()
    total_reviewed = PoliceRecord.query.count()
    active_cases = Case.query.filter(Case.status.in_(['open', 'in_progress'])).all()
    case_backlog = Case.query.filter_by(status='open').count()
    closed_cases = Case.query.filter_by(status='closed').count()

    return render_template('inspector_dashboard.html', pending=pending_records, approved=approved_records,
                         total_reviewed=total_reviewed, active_cases=active_cases,
                         case_backlog=case_backlog, closed_cases=closed_cases)

@app.route('/constable-dashboard')
@login_required
def constable_dashboard():
    if current_user.role != 'constable':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    # Constables see cases assigned to their lead officer? Or explicitly assigned?
    # For now, show cases where they are assigned (even if support)
    case_query = Case.query.join(CaseAssignment).filter(
        CaseAssignment.officer_id == current_user.id
    ).distinct()
    
    assigned_cases = case_query.all()
    total_assigned = len(assigned_cases)
    
    return render_template('constable_dashboard.html', assigned_cases=assigned_cases, total_assigned=total_assigned)


@app.route('/add-record', methods=['GET', 'POST'])
@login_required
def add_record():
    if current_user.role != 'officer':
        flash('Only officers can file reports', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            cleaned, form_values, errors = validate_record_form(request.form)
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('add_record.html', form_data=form_values)

            # Auto-generate case number if not provided
            if not cleaned.get('case_number'):
                year = datetime.utcnow().year
                prefix = f'CASE-{year}-'
                last_record = PoliceRecord.query.filter(PoliceRecord.case_number.like(f'{prefix}%')).order_by(PoliceRecord.case_number.desc()).first()
                
                if last_record:
                    try:
                        last_seq = int(last_record.case_number.split('-')[-1])
                        new_seq = last_seq + 1
                    except ValueError:
                        new_seq = 1
                else:
                    new_seq = 1
                
                cleaned['case_number'] = f'{prefix}{new_seq:04d}'

            record = PoliceRecord(
                **cleaned,
                officer_id=current_user.id,
                status='pending'
            )
            db.session.add(record)
            db.session.commit()
            flash('Record filed successfully', 'success')
            return redirect(url_for('officer_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error filing record: {str(e)}', 'error')

    return render_template('add_record.html', form_data=None, case_types=CASE_TYPES)


@app.route('/view-records')
@login_required
def view_records():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    severity_filter = request.args.get('severity', '').strip()

    # Base query on Case model
    query = Case.query

    # Filter by role
    if current_user.role == 'officer':
        # Officers see cases they are assigned to (lead or support)
        query = query.outerjoin(CaseAssignment).filter(
            or_(
                Case.lead_officer_id == current_user.id,
                CaseAssignment.officer_id == current_user.id
            )
        )
    elif current_user.role in ('inspector', 'admin'):
        # Inspectors and Admins see all cases
        pass
    else:
        # Others see nothing (or handle constables if needed)
        query = query.filter(db.false())

    # Apply filters
    if status_filter:
        query = query.filter(Case.status == status_filter)

    if severity_filter:
        query = query.filter(Case.priority == severity_filter)

    # Apply Search
    if search_query:
        # Transliterate Hindi to English if needed
        transliterated_query = transliterate_to_english(search_query)
        
        # Use both original and transliterated query for better recall
        # If they are same, it just searches once
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

    # Order by newest first
    records = query.order_by(Case.opened_at.desc()).all()

    return render_template(
        'view_records.html',
        records=records,
        search_query=search_query,
        status_filter=status_filter,
        severity_filter=severity_filter,
        fuzzy_used=False, # Fuzzy search temporarily disabled or not needed for simple case search
        fuzzy_scores={}
    )


@app.route('/cases')
@login_required
def cases():
    if current_user.role == 'officer':
        case_query = Case.query.outerjoin(CaseAssignment).filter(
            or_(
                Case.lead_officer_id == current_user.id,
                CaseAssignment.officer_id == current_user.id
            )
        ).distinct()
    else:
        case_query = Case.query

    cases = case_query.order_by(Case.opened_at.desc()).all()
    total_cases = Case.query.count()
    open_cases = Case.query.filter_by(status='open').count()
    in_progress_cases = Case.query.filter_by(status='in_progress').count()
    closed_cases = Case.query.filter_by(status='closed').count()

    return render_template(
        'cases.html',
        cases=cases,
        total_cases=total_cases,
        open_cases=open_cases,
        in_progress_cases=in_progress_cases,
        closed_cases=closed_cases
    )


@app.route('/cases/new', methods=['GET', 'POST'])
@login_required
def create_case():
    if current_user.role not in ('admin', 'inspector'):
        flash('Only admins or inspectors can open cases', 'error')
        return redirect(url_for('cases'))

    officers = User.query.filter(User.role == 'officer').all()

    if request.method == 'POST':
        try:
            # Automatic Case ID Generation
            year = datetime.utcnow().year
            prefix = f'CASE-{year}-'
            last_case = Case.query.filter(Case.case_number.like(f'{prefix}%')).order_by(Case.case_number.desc()).first()
            
            if last_case:
                try:
                    last_seq = int(last_case.case_number.split('-')[-1])
                    new_seq = last_seq + 1
                except ValueError:
                    new_seq = 1
            else:
                new_seq = 1
            
            case_number = f'{prefix}{new_seq:04d}'

            title = request.form.get('title')
            description = request.form.get('description')
            priority = request.form.get('priority') or 'medium'
            status = request.form.get('status') or 'open'
            lead_officer_id = request.form.get('lead_officer_id')

            case = Case(
                case_number=case_number,
                title=title,
                description=description,
                priority=priority,
                status=status,
                lead_officer_id=int(lead_officer_id) if lead_officer_id else None,
            )
            db.session.add(case)
            db.session.commit()
            flash('Case created successfully', 'success')
            return redirect(url_for('case_detail', case_id=case.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating case: {str(e)}', 'error')

    return render_template('case_form.html', officers=officers, case_types=CASE_TYPES)


@app.route('/cases/<int:case_id>')
@login_required
def case_detail(case_id):
    case = Case.query.get_or_404(case_id)
    if not user_can_access_case(case, current_user):
        flash('Access denied', 'error')
        return redirect(url_for('cases'))

    officers = User.query.filter(User.role == 'officer').all()

    return render_template(
        'case_detail.html',
        case=case,
        officers=officers
    )


@app.route('/cases/<int:case_id>/incidents', methods=['POST'])
@login_required
def add_case_incident(case_id):
    case = Case.query.get_or_404(case_id)
    if not user_can_access_case(case, current_user):
        flash('Access denied', 'error')
        return redirect(url_for('cases'))

    try:
        summary = request.form.get('summary')
        incident_type = request.form.get('incident_type')
        location = request.form.get('location')
        incident_date_raw = request.form.get('incident_date')
        incident_date = datetime.strptime(incident_date_raw, '%Y-%m-%dT%H:%M') if incident_date_raw else datetime.utcnow()

        incident = CaseIncident(
            case_id=case.id,
            summary=summary,
            incident_type=incident_type,
            location=location,
            incident_date=incident_date,
            created_by_id=current_user.id
        )
        db.session.add(incident)
        case.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Incident added to case', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding incident: {str(e)}', 'error')

    return redirect(url_for('case_detail', case_id=case.id))


@app.route('/cases/<int:case_id>/firs', methods=['POST'])
@login_required
def add_case_fir(case_id):
    case = Case.query.get_or_404(case_id)
    if not user_can_access_case(case, current_user):
        flash('Access denied', 'error')
        return redirect(url_for('cases'))

    try:
        fir_number = request.form.get('fir_number')
        summary = request.form.get('summary')
        document_link = request.form.get('document_link')
        incident_id = request.form.get('incident_id')

        if not fir_number:
            # Auto-generate FIR number
            year = datetime.utcnow().year
            prefix = f'FIR-{year}-'
            last_fir = FirstInformationReport.query.filter(FirstInformationReport.fir_number.like(f'{prefix}%')).order_by(FirstInformationReport.fir_number.desc()).first()
            
            if last_fir:
                try:
                    last_seq = int(last_fir.fir_number.split('-')[-1])
                    new_seq = last_seq + 1
                except ValueError:
                    new_seq = 1
            else:
                new_seq = 1
            
            fir_number = f'{prefix}{new_seq:04d}'
        elif FirstInformationReport.query.filter_by(fir_number=fir_number).first():
            flash('FIR number already exists', 'error')
            return redirect(url_for('case_detail', case_id=case.id))

        fir = FirstInformationReport(
            case_id=case.id,
            incident_id=int(incident_id) if incident_id else None,
            fir_number=fir_number,
            summary=summary,
            document_link=document_link,
            filed_by_id=current_user.id
        )
        db.session.add(fir)
        case.status = 'in_progress'
        case.updated_at = datetime.utcnow()
        db.session.commit()
        flash('FIR added to case', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding FIR: {str(e)}', 'error')

    return redirect(url_for('case_detail', case_id=case.id))


@app.route('/cases/<int:case_id>/evidence', methods=['POST'])
@login_required
def add_case_evidence(case_id):
    case = Case.query.get_or_404(case_id)
    if not user_can_access_case(case, current_user):
        flash('Access denied', 'error')
        return redirect(url_for('cases'))

    try:
        description = request.form.get('description')
        storage_link = request.form.get('storage_link')
        file_name = request.form.get('file_name')
        incident_id = request.form.get('incident_id')

        evidence = CaseEvidence(
            case_id=case.id,
            incident_id=int(incident_id) if incident_id else None,
            description=description,
            storage_link=storage_link,
            file_name=file_name,
            uploaded_by_id=current_user.id
        )
        db.session.add(evidence)
        case.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Evidence item attached', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding evidence: {str(e)}', 'error')

    return redirect(url_for('case_detail', case_id=case.id))


@app.route('/cases/<int:case_id>/fir/<int:fir_id>/approve', methods=['POST'])
@login_required
@inspector_required
def approve_fir(case_id, fir_id):
    fir = FirstInformationReport.query.get_or_404(fir_id)
    if fir.case_id != case_id:
        abort(404)
    
    # Logic to approve FIR
    # For now, let's log it and update case status if needed.
    # Assuming approval moves case to 'investigating'
    case = Case.query.get(case_id)
    if case.status == 'open':
        case.status = 'in_progress' # or investigating
    
    log_audit('approve_fir', 'fir', fir.id, f"Approved FIR {fir.fir_number}")
    flash('FIR approved successfully', 'success')
    return redirect(url_for('case_detail', case_id=case_id))

@app.route('/cases/<int:case_id>/evidence/<int:evidence_id>/verify', methods=['POST'])
@login_required
@inspector_required
def verify_evidence(case_id, evidence_id):
    evidence = CaseEvidence.query.get_or_404(evidence_id)
    if evidence.case_id != case_id:
        abort(404)
        
    evidence.verified_by_id = current_user.id
    evidence.is_locked = True
    db.session.commit()
    
    log_audit('verify_evidence', 'evidence', evidence.id, f"Verified evidence {evidence.file_name}")
    flash('Evidence verified and locked', 'success')
    return redirect(url_for('case_detail', case_id=case_id))


@app.route('/cases/<int:case_id>/evidence/<int:evidence_id>/custody', methods=['POST'])
@login_required
def add_custody_event(case_id, evidence_id):
    case = Case.query.get_or_404(case_id)
    evidence = CaseEvidence.query.get_or_404(evidence_id)

    if evidence.case_id != case.id:
        flash('Evidence does not belong to this case', 'error')
        return redirect(url_for('case_detail', case_id=case.id))

    if not user_can_access_case(case, current_user):
        flash('Access denied', 'error')
        return redirect(url_for('cases'))

    try:
        from_person = request.form.get('from_person')
        to_person = request.form.get('to_person')
        method = request.form.get('method')
        notes = request.form.get('notes')

        if not to_person:
            flash('Recipient is required for custody transfer', 'error')
            return redirect(url_for('case_detail', case_id=case.id))

        event = CustodyEvent(
            evidence_id=evidence.id,
            from_person=from_person or 'Unknown',
            to_person=to_person,
            method=method,
            notes=notes,
            recorded_by_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Custody event recorded', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error recording custody event: {str(e)}', 'error')

    return redirect(url_for('case_detail', case_id=case.id))


@app.route('/cases/<int:case_id>/assignments', methods=['POST'])
@login_required
def add_case_assignment(case_id):
    case = Case.query.get_or_404(case_id)
    if current_user.role not in ('admin', 'inspector'):
        flash('Only admins or inspectors can assign officers', 'error')
        return redirect(url_for('case_detail', case_id=case.id))

    try:
        officer_id = request.form.get('officer_id')
        role = request.form.get('role') or 'support'
        notes = request.form.get('notes')

        assignment = CaseAssignment(
            case_id=case.id,
            officer_id=int(officer_id),
            role=role,
            notes=notes
        )
        db.session.add(assignment)
        case.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Officer assigned to case', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error assigning officer: {str(e)}', 'error')

    return redirect(url_for('case_detail', case_id=case.id))


@app.route('/cases/<int:case_id>/status', methods=['POST'])
@login_required
def update_case_status(case_id):
    case = Case.query.get_or_404(case_id)
    if not user_can_access_case(case, current_user):
        flash('Access denied', 'error')
        return redirect(url_for('cases'))

    new_status = request.form.get('status')
    allowed_status = {'open', 'in_progress', 'closed'}
    if new_status not in allowed_status:
        flash('Invalid status value', 'error')
        return redirect(url_for('case_detail', case_id=case.id))

    try:
        case.status = new_status
        case.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Case status updated', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating case status: {str(e)}', 'error')

    return redirect(url_for('case_detail', case_id=case.id))


def case_duration_query():
    return db.session.query(
        Case.id,
        Case.opened_at,
        Case.updated_at,
        Case.status
    )


@app.route('/analytics')
@login_required
def analytics_dashboard():
    # Basic Counts
    total_cases = Case.query.count()
    open_cases = Case.query.filter_by(status='open').count()
    in_progress_cases = Case.query.filter_by(status='in_progress').count()
    closed_cases = Case.query.filter_by(status='closed').count()
    
    # Derived Metrics
    active_cases = open_cases + in_progress_cases
    clearance_rate = (closed_cases / total_cases * 100) if total_cases > 0 else 0
    
    # Records Stats
    total_records = PoliceRecord.query.count()
    pending_records = PoliceRecord.query.filter_by(status='pending').count()

    # Case Duration
    average_case_age = None
    if total_cases:
        durations = [
            (datetime.utcnow() - case.opened_at).total_seconds() / 3600
            for case in Case.query.all()
        ]
        average_case_age = sum(durations) / len(durations) if durations else 0

    # Cases by Type (Aggregated from Incidents)
    # This is a bit complex because type is on Incident, not Case directly in some models, 
    # but we can infer from the first incident or title if needed. 
    # For now, let's assume we want to count by the 'incident_type' of the primary incident.
    cases_by_type = {}
    all_cases = Case.query.all()
    for case in all_cases:
        # Try to get type from first incident
        c_type = "Unknown"
        if case.incidents:
            c_type = case.incidents[0].incident_type or "Unknown"
        
        cases_by_type[c_type] = cases_by_type.get(c_type, 0) + 1

    incidents_per_case = db.session.query(
        Case.id,
        func.count(CaseIncident.id).label('incident_count')
    ).outerjoin(CaseIncident).group_by(Case.id).all()

    evidence_per_case = db.session.query(
        Case.id,
        func.count(CaseEvidence.id).label('evidence_count')
    ).outerjoin(CaseEvidence).group_by(Case.id).all()

    fir_counts = db.session.query(
        func.strftime('%Y-%m', FirstInformationReport.filed_at).label('month'),
        func.count(FirstInformationReport.id)
    ).group_by('month').order_by('month').all()

    off_load = db.session.query(
        User.full_name,
        func.count(CaseAssignment.id)
    ).join(CaseAssignment).group_by(User.full_name).all()

    incident_trend = db.session.query(
        func.strftime('%Y-%m', CaseIncident.incident_date).label('month'),
        func.count(CaseIncident.id)
    ).group_by('month').order_by('month').all()

    return render_template(
        'analytics_dashboard.html',
        total_cases=total_cases,
        open_cases=open_cases,
        in_progress_cases=in_progress_cases,
        closed_cases=closed_cases,
        total_records=total_records,
        pending_records=pending_records,
        average_case_age=round(average_case_age, 1) if average_case_age is not None else 0,
        incidents_per_case=incidents_per_case,
        evidence_per_case=evidence_per_case,
        fir_counts=fir_counts,
        officer_workload=off_load,
        incident_trend=incident_trend
    )


@app.route('/record/<int:record_id>/approve', methods=['POST'])
@login_required
def approve_record(record_id):
    if current_user.role != 'inspector':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    record = PoliceRecord.query.get(record_id)
    if record:
        record.status = 'approved'
        db.session.commit()
        flash('Record approved', 'success')
    return redirect(url_for('inspector_dashboard'))


@app.route('/record/<int:record_id>/close', methods=['POST'])
@login_required
def close_record(record_id):
    if current_user.role != 'inspector' and current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    record = PoliceRecord.query.get(record_id)
    if record:
        record.status = 'closed'
        db.session.commit()
        flash('Record closed', 'success')
    return redirect(url_for('view_records'))


@app.route('/record/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    record = PoliceRecord.query.get(record_id)
    if not record:
        flash('Record not found', 'error')
        return redirect(url_for('view_records'))

    can_delete = False
    if current_user.role == 'admin':
        can_delete = True
    elif current_user.role == 'officer' and record.officer_id == current_user.id and record.status == 'pending':
        can_delete = True

    if not can_delete:
        flash('Access denied', 'error')
        return redirect(url_for('view_records'))

    try:
        db.session.delete(record)
        db.session.commit()
        flash('Record deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting record: {str(e)}', 'error')

    return redirect(url_for('view_records'))


@app.route('/manage-users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('user_management.html', users=users)


@app.route('/add-user', methods=['POST'])
@login_required
@admin_required
def add_user():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        full_name = request.form.get('full_name')
        badge_number = request.form.get('badge_number')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('manage_users'))

        user = User(username=username, role=role, full_name=full_name, badge_number=badge_number)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding user: {str(e)}', 'error')

    return redirect(url_for('manage_users'))


@app.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user and user.id != current_user.id:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted', 'success')
    return redirect(url_for('manage_users'))

@app.route('/update-record/<int:record_id>', methods=['GET', 'POST'])
@login_required
def update_record(record_id):
    record = PoliceRecord.query.get(record_id)
    if not record:
        flash('Record not found', 'error')
        return redirect(url_for('dashboard'))

    if current_user.role != 'officer' or record.officer_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            cleaned, form_values, errors = validate_record_form(request.form, record_id=record.id)
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('update_record.html', record=record, form_data=form_values)

            for key, value in cleaned.items():
                setattr(record, key, value)

            db.session.commit()
            flash('Record updated successfully', 'success')
            return redirect(url_for('officer_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating record: {str(e)}', 'error')

    return render_template('update_record.html', record=record, form_data=None)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default users
        if User.query.count() == 0:
            admin = User(username='admin', role='admin', full_name='Admin User', badge_number='ADM001')
            admin.set_password('admin123')

            officer = User(username='officer1', role='officer', full_name='Officer John', badge_number='OFF001')
            officer.set_password('pass123')

            inspector = User(username='inspector1', role='inspector', full_name='Inspector Sarah', badge_number='INS001')
            inspector.set_password('pass123')

            db.session.add(admin)
            db.session.add(officer)
            db.session.add(inspector)
            db.session.commit()

    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)
