from app import app, User

def check_hashes():
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"User: {user.username}, Hash: {user.password[:20]}...")

if __name__ == '__main__':
    check_hashes()
