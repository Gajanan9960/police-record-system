from app import create_app, db
from app.models import Case
import re

app = create_app()

def update_ids():
    with app.app_context():
        print("Starting Case ID migration...")
        cases = Case.query.all()
        count = 0
        
        # Regex to match old format: CASE-{digits}-{year}-{digits}
        # e.g., CASE-1-2025-001
        old_pattern = re.compile(r"CASE-(\d+)-(\d{4})-(\d+)")
        
        for case in cases:
            match = old_pattern.match(case.case_number)
            if match:
                station_id, year, sequence = match.groups()
                new_id = f"CASE-{year}-{sequence}"
                
                if case.case_number != new_id:
                    print(f"Updating {case.case_number} -> {new_id}")
                    case.case_number = new_id
                    count += 1
            else:
                print(f"Skipping {case.case_number} (Does not match old format)")
        
        if count > 0:
            try:
                db.session.commit()
                print(f"Successfully updated {count} cases.")
            except Exception as e:
                db.session.rollback()
                print(f"Error during commit: {e}")
        else:
            print("No cases needed updating.")

if __name__ == "__main__":
    update_ids()
