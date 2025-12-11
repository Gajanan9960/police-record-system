from app import create_app, db
from app.models import User, Station

app = create_app()

def seed():
    with app.app_context():
        print("Seeding data...")
        
        # Create Default Station
        station = Station.query.first()
        if not station:
            station = Station(
                name="Central Police Station",
                address="123 Main St, City Center",
                contact_info="022-12345678",
                fir_prefix_format="FIR-{year}-{num}"
            )
            db.session.add(station)
            db.session.commit()
            print(f"Created Station: {station.name}")
        
        # Create Users
        users_data = [
            {'username': 'admin', 'email': 'admin@police.gov', 'role': 'admin', 'full_name': 'System Admin', 'badge': 'ADM-001'},
            {'username': 'sho', 'email': 'sho@police.gov', 'role': 'sho', 'full_name': 'Station Head Officer', 'badge': 'SHO-001'},
            {'username': 'inspector', 'email': 'inspector@police.gov', 'role': 'inspector', 'full_name': 'Inspector Gadget', 'badge': 'INS-001'},
            {'username': 'io', 'email': 'io@police.gov', 'role': 'io', 'full_name': 'Investigating Officer', 'badge': 'IO-001'},
            {'username': 'officer', 'email': 'officer@police.gov', 'role': 'officer', 'full_name': 'Officer Judy', 'badge': 'OFF-001'},
            {'username': 'clerk', 'email': 'clerk@police.gov', 'role': 'clerk', 'full_name': 'Front Desk Clerk', 'badge': 'CLK-001'},
            {'username': 'malkhana', 'email': 'malkhana@police.gov', 'role': 'malkhana', 'full_name': 'Evidence Custodian', 'badge': 'MAL-001'},
            {'username': 'forensic', 'email': 'forensic@police.gov', 'role': 'forensic', 'full_name': 'Lab Technician', 'badge': 'FOR-001'},
            {'username': 'court', 'email': 'court@police.gov', 'role': 'court', 'full_name': 'Public Prosecutor', 'badge': 'CRT-001'},
        ]

        for user_data in users_data:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    full_name=user_data['full_name'],
                    badge_number=user_data['badge'],
                    station_id=station.id # Link to Station
                )
                user.set_password(f"{user_data['username']}123")
                db.session.add(user)
                print(f"Created user: {user.username}")
        
        db.session.commit()
        
        # Assign Hierarchy (Officer -> Inspector)
        inspector = User.query.filter_by(role='inspector').first()
        officer = User.query.filter_by(role='officer').first()
        io = User.query.filter_by(role='io').first()
        
        if inspector and officer:
            officer.inspector_id = inspector.id
            print(f"Assigned {officer.username} to {inspector.username}")
            
        if inspector and io:
             io.inspector_id = inspector.id
             print(f"Assigned {io.username} to {inspector.username}")

        db.session.commit()
        print("Database seeded successfully.")

if __name__ == '__main__':
    seed()
