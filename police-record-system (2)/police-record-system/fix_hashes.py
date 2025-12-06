from app import app, db, User
from werkzeug.security import generate_password_hash

def fix_hashes():
    with app.app_context():
        users = User.query.all()
        fixed_count = 0
        for user in users:
            if user.password.startswith('scrypt:'):
                print(f"Updating password for user: {user.username}")
                # Resetting to default password 'password123' with new hash method
                user.password = generate_password_hash('password123', method='pbkdf2:sha256')
                fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print(f"Successfully updated {fixed_count} users.")
        else:
            print("No users found with scrypt hashes.")

if __name__ == '__main__':
    fix_hashes()
