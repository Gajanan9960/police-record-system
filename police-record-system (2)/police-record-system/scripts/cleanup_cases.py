from app import app, db, Case, PoliceRecord
import re

def cleanup():
    with app.app_context():
        print("Starting cleanup of invalid case numbers...")
        
        # Regex for valid format: CASE-YYYY-NNNN
        # We'll be a bit flexible and allow any number of digits at the end, but must start with CASE-YYYY-
        valid_pattern = re.compile(r'^CASE-\d{4}-\d+$')
        
        # 1. Cleanup Cases
        cases = Case.query.all()
        deleted_cases = 0
        for case in cases:
            if not valid_pattern.match(case.case_number):
                print(f"Deleting invalid Case: {case.case_number} (ID: {case.id})")
                db.session.delete(case)
                deleted_cases += 1
        
        # 2. Cleanup PoliceRecords
        records = PoliceRecord.query.all()
        deleted_records = 0
        for record in records:
            if record.case_number and not valid_pattern.match(record.case_number):
                print(f"Deleting invalid PoliceRecord: {record.case_number} (ID: {record.id})")
                db.session.delete(record)
                deleted_records += 1
                
        if deleted_cases > 0 or deleted_records > 0:
            db.session.commit()
            print(f"Cleanup complete. Deleted {deleted_cases} Cases and {deleted_records} PoliceRecords.")
        else:
            print("No invalid records found.")

if __name__ == '__main__':
    cleanup()
