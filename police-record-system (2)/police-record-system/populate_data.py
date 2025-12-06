from app import app, db, User, Case, FirstInformationReport, CaseIncident, CaseAssignment, CaseEvidence
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def get_next_case_number():
    year = datetime.utcnow().year
    prefix = f'CASE-{year}-'
    last_case = Case.query.filter(Case.case_number.like(f'{prefix}%')).order_by(Case.case_number.desc()).first()
    
    if last_case:
        try:
            last_seq = int(last_case.case_number.split('-')[-1])
            new_seq = last_seq + 1
        except ValueError:
            new_seq = 1
    else:
        new_seq = 1
    
    return f'{prefix}{new_seq:04d}'

def populate():
    with app.app_context():
        print("Starting data population...")
        
        # 1. Create Users
        users_to_create = [
            {
                'username': 'inspector_nanded',
                'email': 'inspector.nanded@police.gov.in',
                'password': 'password123',
                'role': 'inspector',
                'full_name': 'Inspector Nanded',
                'badge_number': 'MH26-INS-001'
            },
            {
                'username': 'officer_patil',
                'email': 'patil@police.gov.in',
                'password': 'password123',
                'role': 'officer',
                'full_name': 'Officer Patil',
                'badge_number': 'MH26-OFF-101'
            },
            {
                'username': 'officer_deshmukh',
                'email': 'deshmukh@police.gov.in',
                'password': 'password123',
                'role': 'officer',
                'full_name': 'Officer Deshmukh',
                'badge_number': 'MH26-OFF-102'
            }
        ]

        created_users = {}
        for user_data in users_to_create:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    full_name=user_data['full_name'],
                    badge_number=user_data['badge_number']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"Created user: {user.username}")
            else:
                print(f"User already exists: {user.username}")
            created_users[user_data['username']] = user
        
        db.session.commit()
        
        # Refresh users to get IDs
        for username in created_users:
            created_users[username] = User.query.filter_by(username=username).first()

        inspector = created_users['inspector_nanded']
        patil = created_users['officer_patil']
        deshmukh = created_users['officer_deshmukh']

        # 2. Create Cases
        cases_data = [
            {
                'title': 'Theft at Shivaji Nagar Market',
                'description': 'Report of a stolen motorcycle (Hero Splendor) from the vegetable market parking area. CCTV footage requested from nearby shops.',
                'priority': 'medium',
                'status': 'open',
                'lead_officer': patil,
                'location': 'Shivaji Nagar, Nanded',
                'incident_type': 'Theft',
                'incident_summary': 'Motorcycle theft reported by Mr. Kale. Vehicle number MH-26-AB-1234.',
                'evidence': [
                    {'file_name': 'CCTV Footage', 'description': 'CCTV footage from Shop No. 12 showing the suspect taking the bike.', 'storage_link': 'http://evidence-store/cctv-123.mp4'},
                    {'file_name': 'Vehicle Registration', 'description': 'Copy of RC book provided by owner.', 'storage_link': 'http://evidence-store/rc-123.pdf'}
                ]
            },
            {
                'title': 'Assault in Vazirabad',
                'description': 'Physical altercation between two groups near the bus stand. Three individuals sustained minor injuries. Statements being recorded.',
                'priority': 'high',
                'status': 'in_progress',
                'lead_officer': deshmukh,
                'location': 'Vazirabad, Nanded',
                'incident_type': 'Assault',
                'incident_summary': 'Public disturbance and assault. FIR filed.',
                'evidence': [
                    {'file_name': 'Witness Statement', 'description': 'Written statement from eye witness Mr. Pawar.', 'storage_link': 'http://evidence-store/stmt-pawar.pdf'},
                    {'file_name': 'Medical Report', 'description': 'Medical report of the injured victims from Civil Hospital.', 'storage_link': 'http://evidence-store/med-report-456.pdf'}
                ]
            },
            {
                'title': 'Cyber Fraud Complaint',
                'description': 'Complainant reported unauthorized transaction of Rs. 50,000 from their SBI account. Phishing link suspected.',
                'priority': 'high',
                'status': 'open',
                'lead_officer': patil,
                'location': 'Online / Nanded City',
                'incident_type': 'Cyber Crime',
                'incident_summary': 'Online banking fraud reported.',
                'evidence': [
                    {'file_name': 'Bank Statement', 'description': 'SBI Bank statement showing unauthorized debit.', 'storage_link': 'http://evidence-store/bank-stmt-789.pdf'},
                    {'file_name': 'Phishing SMS', 'description': 'Screenshot of the phishing SMS received by the victim.', 'storage_link': 'http://evidence-store/sms-screenshot.jpg'}
                ]
            },
            {
                'title': 'Drug Bust at Railway Station',
                'description': 'Seizure of 500g of Ganja from a suspect near platform 4. Suspect detained and sample sent for forensic analysis.',
                'priority': 'high',
                'status': 'in_progress',
                'lead_officer': inspector,
                'location': 'Railway Station, Nanded',
                'incident_type': 'Drug Offense',
                'incident_summary': 'Narcotics seizure under NDPS Act.',
                'evidence': [
                    {'file_name': 'Seizure Panchnama', 'description': 'Panchnama recorded at the spot of seizure.', 'storage_link': 'http://evidence-store/panchnama-ndps.pdf'},
                    {'file_name': 'Forensic Request', 'description': 'Copy of letter sent to Forensic Lab for chemical analysis.', 'storage_link': 'http://evidence-store/fsl-req.pdf'}
                ]
            },
            {
                'title': 'Hit and Run on Highway',
                'description': 'Speeding truck hit a pedestrian near the bypass junction. Victim hospitalized. Truck number identified from dashcam footage.',
                'priority': 'high',
                'status': 'open',
                'lead_officer': deshmukh,
                'location': 'Nanded-Hyderabad Highway',
                'incident_type': 'Traffic Violation',
                'incident_summary': 'Hit and run case registered under MV Act.',
                'evidence': [
                    {'file_name': 'Dashcam Footage', 'description': 'Video footage from a passing car showing the truck hitting the victim.', 'storage_link': 'http://evidence-store/dashcam-hitrun.mp4'},
                    {'file_name': 'Truck Photo', 'description': 'Still image of the truck license plate extracted from footage.', 'storage_link': 'http://evidence-store/truck-plate.jpg'}
                ]
            },
            {
                'title': 'Domestic Violence Report',
                'description': 'Complaint filed by Mrs. Jadhav regarding physical abuse by her husband. Medical examination conducted.',
                'priority': 'medium',
                'status': 'open',
                'lead_officer': patil,
                'location': 'Anand Nagar, Nanded',
                'incident_type': 'Assault',
                'incident_summary': 'Domestic violence complaint under IPC 498A.',
                'evidence': [
                    {'file_name': 'Medical Examination', 'description': 'Injury report from the government hospital.', 'storage_link': 'http://evidence-store/med-dv.pdf'},
                    {'file_name': 'Neighbor Statement', 'description': 'Statement recorded from the neighbor who heard the altercation.', 'storage_link': 'http://evidence-store/neighbor-stmt.pdf'}
                ]
            },
            {
                'title': 'Shop Shoplifting',
                'description': 'Shop owner caught a teenager stealing electronic accessories. Goods recovered on the spot.',
                'priority': 'low',
                'status': 'closed',
                'lead_officer': deshmukh,
                'location': 'Sarafa Bazar, Nanded',
                'incident_type': 'Theft',
                'incident_summary': 'Minor theft reported and resolved.',
                'evidence': [
                    {'file_name': 'Recovered Goods', 'description': 'Photo of the recovered electronic accessories.', 'storage_link': 'http://evidence-store/goods-photo.jpg'},
                    {'file_name': 'Confession Letter', 'description': 'Written apology and confession from the accused teenager.', 'storage_link': 'http://evidence-store/confession.pdf'}
                ]
            }
        ]

        for case_data in cases_data:
            # Check if similar case exists to avoid duplicates on re-run (simple check by title)
            existing_case = Case.query.filter_by(title=case_data['title']).first()
            if not existing_case:
                case_num = get_next_case_number()
                case = Case(
                    case_number=case_num,
                    title=case_data['title'],
                    description=case_data['description'],
                    priority=case_data['priority'],
                    status=case_data['status'],
                    lead_officer_id=case_data['lead_officer'].id,
                    opened_at=datetime.utcnow() - timedelta(days=1) # Backdate slightly
                )
                db.session.add(case)
                db.session.commit() # Commit to save case and get ID
                print(f"Created case: {case.case_number} - {case.title}")

                # Add Incident
                incident = CaseIncident(
                    case_id=case.id,
                    incident_type=case_data['incident_type'],
                    summary=case_data['incident_summary'],
                    location=case_data['location'],
                    created_by_id=inspector.id,
                    incident_date=datetime.utcnow() - timedelta(days=2)
                )
                db.session.add(incident)
                
                # Add FIR (for some cases)
                if case_data['priority'] == 'high':
                    fir = FirstInformationReport(
                        case_id=case.id,
                        incident_id=incident.id, # Will be None until commit if we don't flush, but let's commit after loop
                        fir_number=f"FIR-{case.case_number}",
                        summary=f"FIR for {case.title}",
                        filed_by_id=case_data['lead_officer'].id,
                        filed_at=datetime.utcnow()
                    )
                    db.session.add(fir)

                # Assign Workload
                assignment = CaseAssignment(
                    case_id=case.id,
                    officer_id=case_data['lead_officer'].id,
                    role='lead',
                    status='active',
                    notes='Assigned as lead investigator.',
                    assigned_at=datetime.utcnow()
                )
                db.session.add(assignment)

                # Add Evidence
                if 'evidence' in case_data:
                    for ev_data in case_data['evidence']:
                        evidence = CaseEvidence(
                            case_id=case.id,
                            incident_id=incident.id,
                            file_name=ev_data['file_name'],
                            description=ev_data['description'],
                            storage_link=ev_data.get('storage_link', ''),
                            uploaded_by_id=case_data['lead_officer'].id,
                            created_at=datetime.utcnow()
                        )
                        db.session.add(evidence)
                
                db.session.commit()
            else:
                print(f"Case already exists: {case_data['title']}")
                case = existing_case
                # Ensure evidence is added if missing
                if 'evidence' in case_data:
                    for ev_data in case_data['evidence']:
                        # Check if this specific evidence already exists
                        existing_ev = CaseEvidence.query.filter_by(case_id=case.id, file_name=ev_data['file_name']).first()
                        if not existing_ev:
                            # We need an incident ID. Try to find the incident for this case.
                            incident = CaseIncident.query.filter_by(case_id=case.id).first()
                            
                            evidence = CaseEvidence(
                                case_id=case.id,
                                incident_id=incident.id if incident else None,
                                file_name=ev_data['file_name'],
                                description=ev_data['description'],
                                storage_link=ev_data.get('storage_link', ''),
                                uploaded_by_id=case.lead_officer_id, # Use lead officer as uploader
                                created_at=datetime.utcnow()
                            )
                            db.session.add(evidence)
                            print(f"Added missing evidence: {ev_data['file_name']}")
                    db.session.commit()

        print("Data population completed successfully.")

if __name__ == '__main__':
    populate()
