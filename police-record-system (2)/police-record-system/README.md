# Police Record Management System

A secure, modular, and efficient system for managing police records, cases, FIRs, and criminal data.

## Features
- **Role-Based Access Control (RBAC)**: Admin, Inspector, and Officer roles with specific permissions.
- **Case Management**: Create, update, and track cases with status and priority.
- **FIR Filing**: File First Information Reports linked to specific cases.
- **Criminal Database**: Manage criminal records with photos and details.
- **Search**: Fuzzy search capabilities including Hindi name transliteration.
- **Security**: CSRF protection, secure password hashing, and role-based route protection.

## Tech Stack
- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate
- **Database**: SQLite (Development)
- **Frontend**: Jinja2 Templates, Tailwind CSS (CDN)

## Setup Instructions

### 1. Clone & Install
```bash
git clone <repository-url>
cd police-record-system
pip install -r requirements.txt
```

### 2. Configuration
Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```
Update `SECRET_KEY`, `MAIL_USERNAME`, etc. in `.env`.

### 3. Database Setup
Initialize and seed the database:
```bash
export FLASK_APP=run.py
flask db upgrade
python seed_data.py
```

### 4. Run Application
```bash
flask runqww
```
Access the app at `http://localhost:5000`.

## Default Users (from seed_data.py)
- **Admin**: `admin` / `admin123`
- **Inspector**: `inspector` / `inspector123`
- **Officer**: `officer` / `officer123`

## Testing
Run automated tests:
```bash
pytest
```
