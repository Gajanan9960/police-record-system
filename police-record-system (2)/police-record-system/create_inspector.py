from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Check if exists
    u = User.query.filter_by(username='inspector1').first()
    if not u:
        u = User(username='inspector1', email='insp1@example.com', role='inspector', full_name='Inspector Manoj Patil', station_id=1, badge_number='INSP001')
        u.set_password('inspector123')
        db.session.add(u)
        db.session.commit()
        print("Created inspector1")
    else:
        print("inspector1 already exists")
