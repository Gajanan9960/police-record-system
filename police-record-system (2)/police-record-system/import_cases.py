import sys
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Station, Case, Participant, Evidence, AuditLog

app = create_app()

def import_cases():
    with app.app_context():
        print("Starting bulk import of MH26 cases...")
        
        # 1. Setup Context
        station = Station.query.get(1)
        if not station:
            print("Error: Station ID 1 not found. Please run seed_data.py first.")
            return

        # Fetch a user to act as creator (e.g., SHO or Inspector)
        creator = User.query.filter_by(role='sho', station_id=1).first()
        if not creator:
             creator = User.query.filter_by(role='admin', station_id=1).first()
        
        if not creator:
            print("Error: No suitable user (SHO/Admin) found to create cases.")
            return
            
        print(f"Using Creator: {creator.username} ({creator.role})")

        # 2. Define Cases Data
        cases_data = [
            {
                "case_number_suffix": "001", # Will append to CASE-{stn}-{year}-
                "title": "Theft of Hero Splendor from Vazirabad Market",
                "offense_type": "Theft",
                "short_description": "Black Hero Splendor Plus stolen from parking area outside Hotel City Pride.",
                "description": "The complainant parked his motorcycle, a Black Hero Splendor Plus (MH-26-BE-1234), outside Hotel City Pride, Vazirabad at approximately 14:00 hours. Upon returning at 15:30 hours, the vehicle was missing. Inquiries with nearby shopkeepers yielded no results. CCTV footage from the hotel shows a suspect in a red cap using a master key to unlock the bike and drive away towards Station Road.",
                "incident_date": datetime(2025, 12, 10, 14, 0),
                "location": "Outside Hotel City Pride, Vazirabad, Nanded, Maharashtra",
                "priority": "Medium",
                "status": "Open",
                "ipc_sections": "379",
                "is_cognizable": True,
                "tags": "vehicle-theft, vazirabad-market, master-key",
                "participants": [
                    {"type": "Complainant", "name": "Rajesh Rameshwar Patil", "contact": "9876543210", "address": "Plot 45, Srinagar, Nanded", "details": "Owner of the bike."},
                    {"type": "Suspect", "name": "Unknown Male (Red Cap)", "details": "Seen in CCTV footage heading towards Station Road."}
                ],
                "evidence": [
                    {"description": "CCTV Footage from Hotel City Pride", "collected_at": datetime(2025, 12, 10, 16, 0)}
                ]
            },
            {
                "case_number_suffix": "002",
                "title": "Night Burglary at Electronics Shop in Shivaji Nagar",
                "offense_type": "Burglary",
                "short_description": "Shutters of 'Om Electronics' broken, cash and mobile phones stolen.",
                "description": "During the night patrol, beat marshals noticed the shutter of 'Om Electronics' in Shivaji Nagar was partially open with the lock broken. Owners were informed. Preliminary inventory suggests theft of roughly ₹50,000 in cash from the counter and 12 smartphones (Samsung and Vivo models). Fingerprints have been lifted from the cash drawer handled by the intruders.",
                "incident_date": datetime(2025, 12, 9, 2, 30),
                "location": "Om Electronics, Main Road, Shivaji Nagar, Nanded, Maharashtra",
                "priority": "High",
                "status": "In Progress",
                "ipc_sections": "457, 380",
                "is_cognizable": True,
                "tags": "night-burglary, electronics-theft, shivaji-nagar",
                "participants": [
                    {"type": "Victim", "name": "Suresh Kumar Jain", "contact": "9988776655", "address": "Flat 102, Galaxy Apartment, Shivaji Nagar, Nanded"},
                    {"type": "Witness", "name": "Constable Ajay Rathod (Beat Marshal)", "details": "First responder who noticed the broken lock."}
                ],
                "evidence": [
                    {"description": "Broken Padlock and Clasp", "collected_at": datetime(2025, 12, 9, 3, 15)},
                    {"description": "Fingerprint Samples from Cash Drawer", "collected_at": datetime(2025, 12, 9, 4, 0)}
                ]
            },
            {
                "case_number_suffix": "003",
                "title": "Online Fraud via Fake Electricity Bill Message",
                "offense_type": "Cybercrime",
                "short_description": "Victim defrauded of ₹25,000 via phishing link for electricity bill payment.",
                "description": "The victim received a text message claiming his MSEDCL electricity connection would be disconnected tonight due to unpaid bills. He clicked the link provided and entered his UPI PIN as requested by the support executive on the call. An amount of ₹25,000 was immediately debited from his SBI account. The number traces to a disposable SIM card.",
                "incident_date": datetime(2025, 12, 8, 10, 45),
                "location": "CIDCO Colony, New Nanded, Nanded, Maharashtra",
                "priority": "Medium",
                "status": "In Progress",
                "ipc_sections": "420; 66C, 66D IT Act",
                "is_cognizable": True,
                "tags": "upi-fraud, phishing, cyber-cell",
                "participants": [
                    {"type": "Victim", "name": "Anjali Deshmukh", "contact": "9123456789", "address": "Row House 7, CIDCO, Nanded"},
                    {"type": "Suspect", "name": "Unknown (Phone Holder: 90000xxxxx)", "details": "Traced to a fake ID in West Bengal circle."}
                ],
                "evidence": [
                    {"description": "Screenshots of SMS and UPI Transaction", "collected_at": datetime(2025, 12, 8, 12, 0)},
                    {"description": "Bank Account Statement (PDF)", "collected_at": datetime(2025, 12, 8, 14, 0)}
                ]
            },
            {
                "case_number_suffix": "004",
                "title": "Group Clash and Assault at Gokul Nagar",
                "offense_type": "Assault",
                "short_description": "Clash between two groups over a parking dispute resulting in minor injuries.",
                "description": "A dispute over parking a chaotic Rickshaw turned violent in Gokul Nagar. Two groups of approximately 5-6 youths engaged in a physical altercation using sticks and stones. Three individuals sustained minor head injuries and were taken to Civil Hospital. Glass windows of a nearby tea stall were damaged. The situation was brought under control by the patrolling van.",
                "incident_date": datetime(2025, 12, 11, 9, 15),
                "location": "Near Hanuman Temple, Gokul Nagar, Nanded, Maharashtra",
                "priority": "High",
                "status": "Pending",
                "ipc_sections": "147, 148, 323, 336",
                "is_cognizable": True,
                "tags": "group-clash, public-disorder, gokul-nagar",
                "participants": [
                    {"type": "Complainant", "name": "Vinod Kambli", "contact": "8888888888", "address": "Gokul Nagar, Nanded", "details": "Auto-rickshaw driver involved in dispute."},
                    {"type": "Suspect", "name": "Local Group (Leader: 'Raju')", "details": "Approximately 5 unidentified youths from nearby slum."},
                    {"type": "Victim", "name": "Santosh Waghmare", "details": "Sustained head injury, admitted to Civil Hospital."}
                ],
                "evidence": [
                    {"description": "Recovered Wooden Sticks (2) and Stones", "collected_at": datetime(2025, 12, 11, 9, 45)},
                    {"description": "Medical Report (MLC) of Santosh Waghmare", "collected_at": datetime(2025, 12, 11, 11, 0)}
                ]
            }
        ]

        # 3. Insert Data
        count = 0
        for data in cases_data:
            # Generate Unique Case Number
            # Format: CASE-{StationID}-{Year}-{Suffix} (using suffix from data or auto-increment if we wanted, 
            # but user data implies these are the 'next' cases. Let's force a unique ID to avoid collision if run multiple times)
            year = datetime.now().year
            case_num = f"CASE-{station.id}-{year}-{data['case_number_suffix']}"
            
            # Check exist
            if Case.query.filter_by(case_number=case_num).first():
                print(f"Skipping {case_num}, already exists.")
                continue

            # Create Case
            new_case = Case(
                station_id=station.id,
                case_number=case_num,
                title=data['title'],
                offense_type=data['offense_type'],
                short_description=data['short_description'],
                description=data['description'],
                incident_date=data['incident_date'],
                location=data['location'],
                priority=data['priority'],
                status=data['status'],
                ipc_sections=data['ipc_sections'],
                is_cognizable=data['is_cognizable'],
                tags=data['tags'],
                created_by_id=creator.id
            )
            db.session.add(new_case)
            db.session.flush() # get ID

            # Audit Log: Case Creation
            audit = AuditLog(
                station_id=station.id,
                user_id=creator.id,
                action='CREATE',
                object_type='Case',
                object_id=new_case.id,
                details=f"Imported Case {case_num}: {data['title']}",
                ip_address='127.0.0.1'
            )
            db.session.add(audit)

            # Participants
            for p_data in data['participants']:
                p = Participant(
                    case_id=new_case.id,
                    type=p_data['type'],
                    name=p_data['name'],
                    contact_info=p_data.get('contact'),
                    address=p_data.get('address'),
                    details=p_data.get('details')
                )
                db.session.add(p)

            # Evidence
            for e_data in data['evidence']:
                e = Evidence(
                    station_id=station.id,
                    case_id=new_case.id,
                    description=e_data['description'],
                    collected_at=e_data['collected_at'],
                    type='Physical' if 'Stick' in e_data['description'] or 'Lock' in e_data['description'] else 'Digital', # Simple inference
                    status='In Custody'
                )
                db.session.add(e)
                db.session.flush()
                
                # Audit for Evidence
                e_audit = AuditLog(
                    station_id=station.id,
                    user_id=creator.id,
                    action='ADD_EVIDENCE',
                    object_type='Evidence',
                    object_id=e.id,
                    details=f"Added evidence to Case {case_num}: {e_data['description']}",
                    ip_address='127.0.0.1'
                )
                db.session.add(e_audit)

            count += 1
            print(f"Prepared Case: {case_num}")

        # 4. Commit
        try:
            db.session.commit()
            print(f"Successfully imported {count} cases.")
        except Exception as e:
            db.session.rollback()
            print(f"Import failed: {e}")

if __name__ == "__main__":
    import_cases()
