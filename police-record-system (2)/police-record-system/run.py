from app import create_app, db
from app.models import User, Case  # Import models to ensure they are registered

app = create_app()

@app.cli.command("reset-data")
def reset_data():
    """Deletes all cases, FIRs, and related transactional data."""
    from app.models import Case, FIR, Evidence, Participant, Statement, InvestigationUpdate, AuditLog, case_officers, case_criminal
    
    print("Resetting data...")
    try:
        # Delete Associations First
        db.session.execute(case_officers.delete())
        db.session.execute(case_criminal.delete())
        
        # Delete Dependents
        db.session.query(InvestigationUpdate).delete()
        db.session.query(Statement).delete()
        db.session.query(Evidence).delete()
        db.session.query(Participant).delete()
        
        # Delete Core Transactional Data
        db.session.query(FIR).delete()
        db.session.query(Case).delete()
        db.session.query(AuditLog).delete()
        
        db.session.commit()
        print("Successfully deleted all Cases, FIRs, Evidence, Participants, Updates, logs, and Links.")
    except Exception as e:
        db.session.rollback()
        print(f"Error resetting data: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
