from app import create_app, db
from app.models import User, Case  # Import models to ensure they are registered

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
