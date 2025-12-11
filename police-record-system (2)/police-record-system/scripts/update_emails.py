from app import app, db, User

def update_all_emails():
    with app.app_context():
        users = User.query.all()
        print(f"Found {len(users)} users.")
        
        for user in users:
            if not user.email:
                # Generate a dummy email based on username
                user.email = f"{user.username}@test.com"
                print(f"Updating {user.username} -> {user.email}")
            else:
                print(f"Skipping {user.username} (already has email: {user.email})")
        
        db.session.commit()
        print("\nAll users updated successfully!")

if __name__ == "__main__":
    update_all_emails()
