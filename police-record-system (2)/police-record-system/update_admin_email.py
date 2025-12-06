from app import app, db, User

def set_real_email():
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        if user:
            user.email = 'sahil.sahu.root@gmail.com'
            db.session.commit()
            print(f"Updated admin email to: {user.email}")
        else:
            print("Admin user not found")

if __name__ == "__main__":
    set_real_email()
