from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    contact_info = db.Column(db.String(100))
    fir_prefix_format = db.Column(db.String(50), default="FIR-{year}-{num}")
    settings = db.Column(db.Text) # JSON string for extra settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(50), nullable=False) # CREATE, UPDATE, DELETE, LOGIN
    object_type = db.Column(db.String(50)) # Case, Evidence, User
    object_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

# Association Table for Case <-> Officer (Many-to-Many Assignment)
case_officers = db.Table('case_officers',
    db.Column('case_id', db.Integer, db.ForeignKey('case.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Roles: clerk, sho, io, malkhana, forensic, court, admin, inspector, officer
    role = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    badge_number = db.Column(db.String(50))
    
    # Hierarchy: Officer reports to Inspector
    inspector_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    station = db.relationship('Station', backref='users')
    officers = db.relationship('User', backref=db.backref('inspector', remote_side=[id]), lazy=True)
    
    cases_reported = db.relationship('Case', foreign_keys='Case.created_by_id', backref='reporter', lazy=True)
    firs_filed = db.relationship('FIR', foreign_keys='FIR.filed_by_id', backref='filer', lazy=True)
    
    # assigned_cases relationship handled via backref in Case (Primary Assignee) and Secondary table (Team)

    def can(self, action, obj=None):
        """
        Checks if user can perform action on object.
        """
        # Admin has full access to their station
        if self.role == 'admin':
            return True
            
        # Station Scope Check
        if obj and hasattr(obj, 'station_id') and obj.station_id != self.station_id:
            return False

        if action == 'view':
            return True # Read-only for all station users (refine as needed)
            
        if action == 'edit':
            if self.role == 'inspector':
                return True
            if self.role == 'officer':
                # Officer can edit if directly assigned or in the team
                if hasattr(obj, 'assigned_officer_id') and obj.assigned_officer_id == self.id:
                    return True
                # Check team assignment
                if hasattr(obj, 'officers') and self in obj.officers:
                    return True
                return False
        
        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    case_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Identification
    title = db.Column(db.String(200), nullable=False)
    
    # Incident Details
    offense_type = db.Column(db.String(100)) # Theft, Assault, Cybercrime
    short_description = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=False) # Detailed Description
    incident_date = db.Column(db.DateTime)
    location = db.Column(db.String(200)) # Address
    gps_coordinates = db.Column(db.String(100)) # "Lat, Long"
    
    # Classification
    status = db.Column(db.String(50), default='Open')  # Open, In Progress, Closed, Court
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    
    # Legal / Procedural
    is_cognizable = db.Column(db.Boolean, default=True)
    ipc_sections = db.Column(db.String(200)) # "302, 307 IPC"
    init_medical_exam = db.Column(db.Boolean, default=False)
    init_prelim_enquiry = db.Column(db.Boolean, default=False)
    init_scene_visit = db.Column(db.Boolean, default=False)
    
    court_status = db.Column(db.String(50)) # Hearing, Verdict Awaited, Closed
    verdict = db.Column(db.Text)
    
    # New Fields (Phase 11.2)
    confidentiality_level = db.Column(db.String(20), default='Public') # Public, Restricted, Confidential
    tags = db.Column(db.Text) # JSON list or comma-separated
    related_case_ids = db.Column(db.Text) # JSON list of IDs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_officer_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Lead Officer/Inspector
    
    # Relationships
    station = db.relationship('Station', backref='cases')
    assignee = db.relationship('User', foreign_keys=[assigned_officer_id], backref='cases_led')
    officers = db.relationship('User', secondary=case_officers, backref='cases_assisted') # Team
    
    criminals = db.relationship('Criminal', secondary='case_criminal', backref=db.backref('cases', lazy=True))
    participants = db.relationship('Participant', backref='case', lazy=True, cascade="all, delete-orphan")
    firs = db.relationship('FIR', backref='case', lazy=True)
    evidence = db.relationship('Evidence', backref='case', lazy=True)
    statements = db.relationship('Statement', backref='case', lazy=True)
    updates = db.relationship('InvestigationUpdate', backref='case', lazy=True)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) # Victim, Suspect, Witness, Complainant
    contact_info = db.Column(db.String(200))
    details = db.Column(db.Text) # Statement or Description
    
    # Enhanced Fields
    dob = db.Column(db.Date)
    address = db.Column(db.Text)
    national_id = db.Column(db.String(50)) # Aadhar/Passport
    status = db.Column(db.String(50)) # For Suspects: Wanted, Arrested
    consent_for_contact = db.Column(db.Boolean, default=True) # For Victims
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FIR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    fir_number = db.Column(db.String(50), unique=True, nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    filed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    details = db.Column(db.Text, nullable=False)
    witnesses = db.Column(db.Text) # JSON or comma-separated
    
    # Approval Workflow
    status = db.Column(db.String(50), default='Pending') # Pending, Approved, Rejected
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    forwarded_to_sho = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    station = db.relationship('Station', backref='firs')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])

class Criminal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    aliases = db.Column(db.String(200))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    address = db.Column(db.Text)
    photo_path = db.Column(db.String(255))
    fingerprint_hash = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Wanted') # Wanted, Arrested, In Custody
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    station = db.relationship('Station', backref='criminals')

# Association Table for Case <-> Criminal
case_criminal = db.Table('case_criminal',
    db.Column('case_id', db.Integer, db.ForeignKey('case.id'), primary_key=True),
    db.Column('criminal_id', db.Integer, db.ForeignKey('criminal.id'), primary_key=True)
)

class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50)) # Physical, Digital, Document
    custodian_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Current holder (Malkhana/IO)
    location = db.Column(db.String(100)) # Shelf A, Server, etc.
    status = db.Column(db.String(50), default='In Custody') # In Custody, Checked Out, Destroyed
    qr_code = db.Column(db.String(100))
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    station = db.relationship('Station', backref='evidence')
    custodian = db.relationship('User', foreign_keys=[custodian_id])

class Statement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    person_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50)) # Witness, Victim, Accused
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    station = db.relationship('Station', backref='statements')
    recorded_by = db.relationship('User', foreign_keys=[recorded_by_id])

class InvestigationUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    station = db.relationship('Station', backref='updates')
    officer = db.relationship('User', foreign_keys=[officer_id])

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    status = db.Column(db.String(50), default='Pending') # Pending, In Progress, Completed, Blocked
    priority = db.Column(db.String(20), default='Medium') # Low, Medium, High
    due_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    case = db.relationship('Case', backref=db.backref('tasks', lazy=True))
    station = db.relationship('Station', backref='tasks')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='tasks_assigned_to')
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id], backref='tasks_created')
