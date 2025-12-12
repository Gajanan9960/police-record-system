from app import create_app, db
from app.models import User

app = create_app()

def migrate_roles():
    with app.app_context():
        # Find all users with role 'sho'
        sho_users = User.query.filter_by(role='sho').all()
        count = 0
        for user in sho_users:
            print(f"Migrating user {user.username} (ID: {user.id}) from SHO to Admin...")
            user.role = 'admin'
            count += 1
        
        if count > 0:
            db.session.commit()
            print(f"Successfully migrated {count} users.")
        else:
            print("No users found with role 'sho'.")

if __name__ == '__main__':
    migrate_roles()
