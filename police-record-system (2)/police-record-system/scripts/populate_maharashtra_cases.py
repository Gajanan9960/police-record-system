import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Case, FIR, Evidence, Statement, InvestigationUpdate, Criminal, Station
from datetime import datetime, timedelta

app = create_app()

def populate():
    with app.app_context():
        print("Populating Maharashtra Cases...")
        
        station = Station.query.first()
        if not station:
            print("Error: No station found. Run seed_data.py first.")
            return

        # Get Users
        admin = User.query.filter_by(role='admin').first()
        sho = User.query.filter_by(role='sho').first()
        io = User.query.filter_by(role='io').first()
        clerk = User.query.filter_by(role='clerk').first()
        malkhana = User.query.filter_by(role='malkhana').first()
        
        if not all([admin, sho, io, clerk]):
            print("Error: Missing required users. Run seed_data.py first.")
            return

        # Case 1: Mumbai Cyber Cell - Online Banking Fraud
        # Status: Investigation
        case1_num = "MUM-CYB-2025-001"
        if not Case.query.filter_by(case_number=case1_num).first():
            case1 = Case(
                case_number=case1_num,
                station_id=station.id,
                title="Unauthorized Withdrawal from SBI Account",
                description="Complainant reported unauthorized deduction of Rs. 50,000 via UPI transaction to an unknown beneficiary.",
                status="In Progress",
                priority="High",
                location="Andheri East, Mumbai",
                created_by_id=sho.id,
                assigned_officer_id=io.id,
                created_at=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(case1)
            db.session.commit()
            
            # FIR
            fir1 = FIR(
                fir_number="FIR-MUM-001",
                station_id=station.id,
                case_id=case1.id,
                filed_by_id=clerk.id,
                details="Victim received a phishing link via SMS. Clicked link, entered PIN. Money deducted.",
                witnesses="None",
                status="Approved",
                approved_by_id=sho.id,
                forwarded_to_sho=True,
                created_at=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(fir1)
            
            # Evidence
            ev1 = Evidence(
                case_id=case1.id,
                station_id=station.id,
                description="Server Logs from Bank",
                type="Digital",
                custodian_id=io.id,
                location="Cyber Cell Server",
                status="In Custody",
                created_at=datetime.utcnow() - timedelta(days=4)
            )
            db.session.add(ev1)
            
            # Statement
            stmt1 = Statement(
                case_id=case1.id,
                station_id=station.id,
                recorded_by_id=io.id,
                person_name="Rahul Sharma (Victim)",
                type="Victim",
                content="I received a message saying my electricity bill is unpaid. I clicked the link and paid Rs 10. Immediately 50k was debited.",
                created_at=datetime.utcnow() - timedelta(days=4)
            )
            db.session.add(stmt1)
            
            # Update
            upd1 = InvestigationUpdate(
                case_id=case1.id,
                station_id=station.id,
                officer_id=io.id,
                description="Traced IP address to a location in Jamtara. Requested ISP details.",
                created_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(upd1)
            print(f"Added Case: {case1.title}")

        # Case 2: Pune City Police - Vehicle Theft
        # Status: Closed/Recovered
        case2_num = "PUN-VEH-2025-042"
        if not Case.query.filter_by(case_number=case2_num).first():
            case2 = Case(
                case_number=case2_num,
                station_id=station.id,
                title="Theft of Honda City Car",
                description="White Honda City (MH 12 AB 1234) stolen from parking lot.",
                status="Closed",
                priority="Medium",
                location="Kothrud, Pune",
                created_by_id=sho.id,
                assigned_officer_id=io.id,
                created_at=datetime.utcnow() - timedelta(days=20),
                updated_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(case2)
            db.session.commit()
            
            fir2 = FIR(
                fir_number="FIR-PUN-042",
                station_id=station.id,
                case_id=case2.id,
                filed_by_id=clerk.id,
                details="Car stolen between 2 AM and 5 AM. CCTV shows two masked men.",
                witnesses="Watchman",
                status="Approved",
                approved_by_id=sho.id,
                forwarded_to_sho=True
            )
            db.session.add(fir2)
            
            ev2 = Evidence(
                case_id=case2.id,
                station_id=station.id,
                description="CCTV Footage",
                type="Digital",
                custodian_id=malkhana.id,
                location="Malkhana Locker 4B",
                status="In Custody"
            )
            db.session.add(ev2)
            
            upd2 = InvestigationUpdate(
                case_id=case2.id,
                station_id=station.id,
                officer_id=io.id,
                description="Vehicle intercepted at toll plaza. Suspects fled. Vehicle recovered.",
                created_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(upd2)
            print(f"Added Case: {case2.title}")

        # Case 3: Nagpur Police - Assault/Rioting
        # Status: Court Trial
        case3_num = "NAG-AST-2025-089"
        if not Case.query.filter_by(case_number=case3_num).first():
            case3 = Case(
                case_number=case3_num,
                station_id=station.id,
                title="Public Brawl at Sitabuldi Market",
                description="Two groups clashed over shop encroachment. 3 injured.",
                status="Court",
                priority="High",
                location="Sitabuldi, Nagpur",
                court_status="Hearing Scheduled",
                created_by_id=sho.id,
                assigned_officer_id=io.id,
                created_at=datetime.utcnow() - timedelta(days=45)
            )
            db.session.add(case3)
            db.session.commit()
            
            fir3 = FIR(
                fir_number="FIR-NAG-089",
                station_id=station.id,
                case_id=case3.id,
                filed_by_id=clerk.id,
                details="Violent clash involving iron rods. Police intervened.",
                witnesses="Shopkeepers Association President",
                status="Approved",
                approved_by_id=sho.id,
                forwarded_to_sho=True
            )
            db.session.add(fir3)
            
            ev3 = Evidence(
                case_id=case3.id,
                station_id=station.id,
                description="Iron Rod (Weapon)",
                type="Physical",
                custodian_id=malkhana.id,
                location="Malkhana Room 1",
                status="Checked Out (Court)"
            )
            db.session.add(ev3)
            
            crim3 = Criminal(
                name="Suresh 'Bhai' Patil",
                station_id=station.id,
                aliases="Suri",
                dob=datetime(1990, 5, 15),
                gender="Male",
                status="Arrested",
                address="Nagpur Slums"
            )
            db.session.add(crim3)
            db.session.commit()
            
            print(f"Added Case: {case3.title}")

        # Case 4: Nashik Rural - Land Dispute/Fraud
        # Status: Pending FIR (Not yet approved by SHO)
        case4_num = "NSK-LND-2025-012"
        if not Case.query.filter_by(case_number=case4_num).first():
            case4 = Case(
                case_number=case4_num,
                station_id=station.id,
                title="Illegal Land Encroachment in Trimbak",
                description="Neighbor built fence on complainant's agricultural land.",
                status="Pending",
                priority="Medium",
                location="Trimbakeshwar, Nashik",
                created_by_id=clerk.id, # Created by clerk
                created_at=datetime.utcnow() - timedelta(hours=2)
            )
            db.session.add(case4)
            db.session.commit()
            
            fir4 = FIR(
                fir_number="FIR-NSK-012",
                station_id=station.id,
                case_id=case4.id,
                filed_by_id=clerk.id,
                details="Dispute over survey number 45/2. Fake documents alleged.",
                witnesses="Talathi (Village Officer)",
                status="Pending",
                forwarded_to_sho=True
            )
            db.session.add(fir4)
            print(f"Added Case: {case4.title}")

        db.session.commit()
        print("Maharashtra Data Population Complete.")

if __name__ == '__main__':
    populate()
