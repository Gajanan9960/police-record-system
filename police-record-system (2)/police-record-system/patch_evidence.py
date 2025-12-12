from app import create_app, db
from app.models import Evidence, Case, User

app = create_app()

def patch_data():
    with app.app_context():
        print("Patching broken Evidence records...")
        evidences = Evidence.query.filter((Evidence.custodian_id == None) | (Evidence.location == None)).all()
        
        count = 0
        for ev in evidences:
            case = Case.query.get(ev.case_id)
            if not case:
                continue
                
            # Set default custodian to Case Creator
            if not ev.custodian_id:
                ev.custodian_id = case.created_by_id
            
            # Set default location
            if not ev.location:
                if ev.type == 'Physical' or 'Stick' in ev.description or 'Lock' in ev.description:
                    ev.location = "Malkhana Room 1"
                else:
                    ev.location = "Pending Upload"
            
            count += 1
            
        if count > 0:
            db.session.commit()
            print(f"Patched {count} evidence records.")
        else:
            print("No records needed patching.")

if __name__ == "__main__":
    patch_data()
