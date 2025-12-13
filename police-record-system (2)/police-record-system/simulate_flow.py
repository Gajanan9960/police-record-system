from app import create_app, db
from app.models import User, Case, FIR
from datetime import datetime

app = create_app()
ctx = app.app_context()
ctx.push()

# 1. Create Clerk if not exists
clerk = User.query.filter_by(role='clerk').first()
if not clerk:
    print("No clerk found!")
    exit(1)

# 2. Register FIR (Simulate Clerk)
print("--- Registering FIR ---")
case = Case(
    case_number=f"TEST-CASE-{int(datetime.utcnow().timestamp())}",
    title="Test Flow Case",
    status='Open', # As per routes.py
    created_by_id=clerk.id,
    station_id=clerk.station_id
)
db.session.add(case)
db.session.commit()

fir = FIR(
    fir_number=f"FIR-{int(datetime.utcnow().timestamp())}",
    case_id=case.id,
    filed_by_id=clerk.id,
    details="Test FIR details",
    status='Pending'
    # forwarded_to_sho defaults to False
)
db.session.add(fir)
db.session.commit()
print(f"Created Case {case.case_number} (Status: {case.status}) and FIR {fir.fir_number} (Forwarded: {fir.forwarded_to_sho})")

# 3. Check Visibility in Admin Dashboard (Before Forward)
# Query from dashboard/routes.py:
# pending_firs_list = station_scoped(FIR.query).filter_by(status='Pending', forwarded_to_sho=True).all()
from app.utils import station_scoped
pending_visible = station_scoped(FIR.query).filter_by(status='Pending', forwarded_to_sho=True).count()
print(f"Visible in Admin Pending Approvals (Before Forward): {pending_visible}")

# 4. Forward FIR
print("--- Forwarding FIR ---")
fir.forwarded_to_sho = True
db.session.commit()
print(f"FIR Forwarded: {fir.forwarded_to_sho}")

# 5. Check Visibility in Admin Dashboard (After Forward)
pending_visible_after = station_scoped(FIR.query).filter_by(status='Pending', forwarded_to_sho=True).count()
print(f"Visible in Admin Pending Approvals (After Forward): {pending_visible_after}")

# 6. Check Visibility in Case Assignment
# Query: active_cases = station_scoped(Case.query).filter(Case.status.in_(['Open', 'In Progress', 'Pending'])).all()
case_visible = station_scoped(Case.query).filter(Case.status.in_(['Open', 'In Progress', 'Pending'])).filter_by(id=case.id).count()
print(f"Visible in Case Assignment: {case_visible}")
