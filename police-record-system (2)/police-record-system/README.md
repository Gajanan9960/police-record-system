# Police Record Management System

A simple and lightweight Flask-based police record management system with role-based dashboards for Admin, Officers, and Inspectors.

## Features

- **Role-Based Access Control**: Three distinct user roles with customized dashboards
  - **Admin**: Manage users, view all records, system overview
  - **Officer**: File new police reports, track their submitted records
  - **Inspector**: Review and approve/reject police reports

- **Police Record Management**: 
  - File new records with incident details, severity levels, and descriptions
  - Track record status (Pending, Approved, Closed)
  - View record history with timestamps
  - Search and filter records

- **Dashboard Features**:
  - Real-time statistics and summary cards
  - Recent activity tracking
  - User management interface (Admin only)
  - Record filtering and sorting

- **Security**:
  - Password hashing using werkzeug
  - Session-based authentication
  - Role-based access control on all routes
  - CSRF protection ready

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (local file-based)
- **Frontend**: HTML5, CSS3, Tailwind CSS
- **Authentication**: Flask-Login

## Project Structure

\`\`\`
police-system/
├── app.py                          # Main Flask application
├── database.db                     # SQLite database (auto-created)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── templates/
│   ├── base.html                  # Base template with navigation
│   ├── login.html                 # Login page
│   ├── admin_dashboard.html       # Admin dashboard
│   ├── officer_dashboard.html     # Officer dashboard
│   ├── inspector_dashboard.html   # Inspector dashboard
│   ├── add_record.html            # Form to file new reports
│   ├── view_records.html          # Records listing page
│   └── user_management.html       # User management (Admin only)
└── static/
    └── style.css                  # Custom styling
\`\`\`

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

\`\`\`bash
pip install flask flask-sqlalchemy flask-login werkzeug
\`\`\`

Or use the requirements file:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Step 2: Run the Application

\`\`\`bash
python app.py
\`\`\`

The application will start on `http://localhost:5000`

### Step 3: Access the System

Open your browser and navigate to `http://localhost:5000`

## Default Test Credentials

The system comes pre-loaded with test users:

| Username | Password | Role |
|----------|----------|------|
| inspector_nanded | password123 | Inspector |
| officer_patil | password123 | Officer |
| officer_deshmukh | password123 | Officer |

**⚠️ Note**: Change these credentials after first login in a production environment.

## User Roles & Permissions

### Admin
- View system dashboard with all statistics
- Manage users (add, delete officers and inspectors)
- View all police records in the system
- Access to all features
- Route: `/admin/dashboard`

### Officer
- File new police reports
- View their own submitted records
- Track record approval status
- Add incident details and severity levels
- Route: `/officer/dashboard`

### Inspector
- Review pending police records
- Approve or reject submitted reports
- Add remarks and comments
- View approved and rejected records
- Route: `/inspector/dashboard`

## Database Schema

### Users Table
\`\`\`
- id (Primary Key)
- username (Unique)
- password (Hashed)
- role (Admin, Officer, Inspector)
- created_at (Timestamp)
\`\`\`

### Police Records Table
\`\`\`
- id (Primary Key)
- officer_id (Foreign Key to User)
- incident_type (e.g., Robbery, Assault, Theft)
- severity (Low, Medium, High, Critical)
- description (Incident details)
- status (Pending, Approved, Closed)
- remarks (Inspector comments)
- created_at (Timestamp)
- updated_at (Timestamp)
\`\`\`

## Key Features & How to Use

### 1. Filing a Police Report (Officer)
1. Login as an Officer
2. Click "File New Report" on dashboard
3. Fill in incident type, severity, and description
4. Submit the report
5. Report will be visible to Inspectors for review

### 2. Reviewing Reports (Inspector)
1. Login as an Inspector
2. View pending reports on dashboard
3. Click "Review" on any report
4. Add remarks and approve/reject
5. Status will update automatically

### 3. Managing Users (Admin)
1. Login as Admin
2. Go to "User Management"
3. Add new Officers or Inspectors
4. View all users and their activity
5. Delete users if needed

### 4. Viewing Records
- Each role can view records relevant to their permissions
- Filter by status (Pending, Approved, Closed)
- Filter by severity (Low, Medium, High, Critical)
- Search by incident type

## Security Notes

- All passwords are hashed using werkzeug security
- Sessions expire when browser closes
- Each route checks user role before allowing access
- Database is local (SQLite) - suitable for development

## Troubleshooting

### Database Issues
If you encounter database errors:
\`\`\`bash
# Delete the old database
rm database.db

# Restart the app
python app.py
\`\`\`
A new database will be created automatically.

### Port Already in Use
If port 5000 is already in use, modify line in `app.py`:
\`\`\`python
app.run(debug=True, port=5001)  # Change to any available port
\`\`\`

### Import Errors
Ensure all dependencies are installed:
\`\`\`bash
pip install --upgrade flask flask-sqlalchemy flask-login werkzeug
\`\`\`

## Future Enhancements

- Email notifications for record updates
- Advanced search and filtering
- Record export to PDF
- Audit logs for all actions
- Multi-department support
- Case assignment system

## License

This project is provided as-is for educational and departmental use.

## Support

For issues or questions, ensure all dependencies are installed and try restarting the application.
