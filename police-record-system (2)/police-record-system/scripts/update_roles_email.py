from app import app, db, User

def update_other_emails():
    with app.app_context():
        # Update Officer
        officer = User.query.filter_by(username='officer1').first()
        if officer:
            officer.email = 'sahil.sahu.root+officer@gmail.com'
            print(f"Updated officer1 email to: {officer.email}")

        # Update Inspector
        inspector = User.query.filter_by(username='inspector1').first()
        if inspector:
            inspector.email = 'sahil.sahu.root+inspector@gmail.com'
            print(f"Updated inspector1 email to: {inspector.email}")
            
        db.session.commit()

if __name__ == "__main__":
    update_other_emails()
