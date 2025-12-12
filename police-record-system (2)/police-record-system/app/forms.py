from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, DateField, FileField, DateTimeField, MultipleFileField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from datetime import datetime, timedelta
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('clerk', 'Clerk'),
        ('sho', 'Station Head Officer (SHO)'),
        ('io', 'Investigating Officer (IO)'),
        ('malkhana', 'Evidence Custodian'),
        ('forensic', 'Forensic Lab'),
        ('court', 'Court Liaison'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    badge_number = StringField('Badge Number')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered.')

class CaseForm(FlaskForm):
    # Identification
    title = StringField('Case Title', validators=[DataRequired(), Length(min=5, max=150)])
    case_number = StringField('Case Number (Auto-assigned if empty)', validators=[Optional(), Length(min=5, max=40)])
    
    # Incident Details
    offense_type = SelectField('Offense Type', choices=[
        ('Theft', 'Theft'), ('Burglary', 'Burglary'), ('Assault', 'Assault'), 
        ('Cybercrime', 'Cybercrime'), ('Fraud', 'Fraud'), ('Homicide', 'Homicide'),
        ('Drug', 'Drug Offense'), ('Other', 'Other')
    ], validators=[DataRequired()])
    short_description = StringField('Short Description', validators=[DataRequired(), Length(min=10, max=255)])
    description = TextAreaField('Detailed Incident Description', validators=[DataRequired(), Length(min=20, max=5000)])
    incident_date = DateTimeField('Date & Time of Occurrence', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location (Address)', validators=[DataRequired(), Length(min=5, max=500)])
    gps_coordinates = StringField('GPS Coordinates', validators=[Optional()]) # Custom validator could be added
    
    # Classification
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Critical', 'Critical')], default='Medium')
    status = SelectField('Initial Status', choices=[
        ('Open', 'Open'), 
        ('In Progress', 'In Progress'), 
        ('Closed', 'Closed'), 
        ('Court', 'Court'),
        ('Pending', 'Pending')
    ], default='Open')
    linked_fir_id = StringField('Linked FIR Number (Optional)', validators=[Optional()])
    related_case_ids = StringField('Related Case IDs (comma separated)', validators=[Optional()])
    
    # Admin
    confidentiality_level = SelectField('Confidentiality', choices=[('Public', 'Public'), ('Restricted', 'Restricted'), ('Confidential', 'Confidential')], default='Public')
    tags = StringField('Tags (comma separated)', validators=[Optional(), Length(max=200)])
    
    # Assignment
    assigned_officer_id = SelectField('Lead Inspector', coerce=int, validators=[Optional()])
    officer_ids = SelectMultipleField('Assign Officers', coerce=int, validators=[Optional()])
    
    # Evidence
    evidence_files = MultipleFileField('Upload Evidence (Photos/Docs)', validators=[Optional()])
    evidence_description = StringField('Evidence Description', validators=[Optional()])
    evidence_collected_at = DateTimeField('Date Evidence Collected', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    
    # Legal
    is_cognizable = SelectField('Offense Category', choices=[('True', 'Cognizable'), ('False', 'Non-Cognizable')], coerce=lambda x: x == 'True')
    ipc_sections = StringField('IPC Sections (comma separated)', validators=[Optional()])
    init_medical_exam = BooleanField('Initiate Medical Examination')
    init_prelim_enquiry = BooleanField('Initiate Preliminary Enquiry')
    init_scene_visit = BooleanField('Initiate Scene Visit')
    
    submit = SubmitField('Create Case')

    def validate_incident_date(self, incident_date):
        if incident_date.data > datetime.utcnow() + timedelta(hours=1):
            raise ValidationError('Incident date cannot be in the future.')
        
        start_allowed_date = datetime.utcnow() - timedelta(days=180) # 6 months
        if incident_date.data < start_allowed_date:
            raise ValidationError('Incident date cannot be older than 6 months.')

    def validate_case_number(self, case_number):
         # If provided, check uniqueness (Optional simple check, real check in route/db)
         if case_number.data:
             from app.models import Case
             # scoped check logic is complex inside form without current_user/context awareness easily
             pass

    def validate_evidence_collected_at(self, evidence_collected_at):
        if evidence_collected_at.data:
            if evidence_collected_at.data > datetime.utcnow() + timedelta(minutes=1): # Small buffer for server time diff
                raise ValidationError('Evidence collection time cannot exceed the current date and time.')
            
            # Note: Cross-field validation vs incident_date is handled in validate()

    def validate(self, extra_validators=None):
        if not super(CaseForm, self).validate(extra_validators):
            return False
        
        # Cross-field validation: Evidence Date vs Incident Date
        if self.evidence_files.data: 
            # Check if actual files were uploaded (Flask-WTF usually has filename if selected)
            # Or relying on evidence_collected_at being optional strictly unless files are there?
            # Simpler: If a date is provided, validate it.
            if self.evidence_collected_at.data and self.incident_date.data:
                if self.evidence_collected_at.data < self.incident_date.data:
                    self.evidence_collected_at.errors.append('Evidence cannot be collected before the incident occurred.')
                    return False
        return True

class FIRForm(FlaskForm):
    fir_number = StringField('FIR Number', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    witnesses = TextAreaField('Witnesses (comma separated)')
    submit = SubmitField('File FIR')


class CriminalForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    aliases = StringField('Aliases')
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = TextAreaField('Address')
    photo = FileField('Photo')
    status = SelectField('Status', choices=[('Wanted', 'Wanted'), ('Arrested', 'Arrested'), ('In Custody', 'In Custody')])
    submit = SubmitField('Add Criminal')
