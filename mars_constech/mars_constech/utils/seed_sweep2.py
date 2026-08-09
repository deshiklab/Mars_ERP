import frappe, json

HANDOVER = [
    {"unit": "Jolshiri - Apt 9A", "customer": "Kamrul Hasan", "project": "Jolshiri", "type": "Apartment", "status": "Inspection Pending", "date": "2025-01-15", "snags": 3, "posDate": "2024-12-20", "tv": 4500000, "paid": 4100000, "remarks": "Pending final inspection", "assigned": "Tanvir Ahmed"},
    {"unit": "Muktodhara - Plot M-103", "customer": "Tariqul Islam", "project": "Muktodhara", "type": "Plot", "status": "Handover Scheduled", "date": "2025-02-01", "snags": 0, "posDate": "2025-01-25", "tv": 8000000, "paid": 7200000, "remarks": "All paperwork ready", "assigned": "Shahidul Islam"},
    {"unit": "Jolshiri - Apt 4B", "customer": "Dr. Rubina Ali", "project": "Jolshiri", "type": "Apartment", "status": "Construction Ongoing", "date": "2025-06-30", "snags": 0, "posDate": "", "tv": 5500000, "paid": 2400000, "remarks": "Expected completion June 2025", "assigned": "Rofiqul Islam"},
    {"unit": "Muktodhara - Unit 201", "customer": "Md. Nazrul Islam", "project": "Muktodhara", "type": "Apartment", "status": "Completed", "date": "2024-12-15", "snags": 2, "posDate": "2024-12-15", "tv": 6000000, "paid": 4500000, "remarks": "Handed over - 2 snags pending", "assigned": "Tanvir Ahmed"},
    {"unit": "Jolshiri - Apt 3C", "customer": "Mrs. Jahanara Begum", "project": "Jolshiri", "type": "Apartment", "status": "Completed", "date": "2024-06-30", "snags": 0, "posDate": "2024-06-30", "tv": 4800000, "paid": 4800000, "remarks": "Fully paid and handed over", "assigned": "Tanvir Ahmed"},
]

VARIATIONS = [
    {"project": "Muktodhara Green Park", "title": "Widening of Drainage", "status": "Approved", "impact": "+৳1,50,000", "originator": "Site Engineer", "date": "2024-09-15", "schedule": "+7 days"},
    {"project": "Jolshiri Abason", "title": "Additional Parking Level", "status": "Pending Review", "impact": "+৳8,00,000", "originator": "Architect", "date": "2024-10-20", "schedule": "+21 days"},
    {"project": "Muktodhara Green Park", "title": "Premium Flooring Upgrade", "status": "Draft", "impact": "+৳3,20,000", "originator": "Client", "date": "2024-10-25", "schedule": "+14 days"},
]

LABOR = [
    {"name": "Md. Rofiqul Islam", "cat": "Skilled Mason", "site": "Muktodhara", "phone": "01711-123456", "sal": 28000, "rating": 5, "join": "2023-01-15"},
    {"name": "Abdur Rashid", "cat": "Rod Binder", "site": "Jolshiri", "phone": "01722-234567", "sal": 24000, "rating": 4, "join": "2023-03-01"},
    {"name": "Shahidul Islam", "cat": "Carpenter", "site": "Muktodhara", "phone": "01733-345678", "sal": 26000, "rating": 4, "join": "2022-11-20"},
    {"name": "Khalilur Rahman", "cat": "General Labor", "site": "Jolshiri", "phone": "01744-456789", "sal": 18000, "rating": 3, "join": "2024-01-10"},
    {"name": "Monir Hossain", "cat": "Electrician", "site": "Muktodhara", "phone": "01755-567890", "sal": 30000, "rating": 5, "join": "2022-06-01"},
]

INVESTMENTS = [
    {"inv": "Abdul Matin", "proj": "Muktodhara", "amt": 20000000, "rate": 15, "start": "2024-04-01", "tenure": 24, "sched": "Monthly"},
    {"inv": "Salma Khatun", "proj": "Jolshiri", "amt": 15000000, "rate": 12, "start": "2024-07-01", "tenure": 36, "sched": "Quarterly"},
    {"inv": "Green Delta Holdings", "proj": "Purbachal Phase 1", "amt": 50000000, "rate": 18, "start": "2024-10-01", "tenure": 24, "sched": "Monthly"},
    {"inv": "Md. Rafiqul Alam", "proj": "Muktodhara Green Park", "amt": 10000000, "rate": 10, "start": "2025-02-01", "tenure": 18, "sched": "Quarterly"},
]

LOANS = [
    {"type": "External", "lender": "Islami Bank BD", "principal": 50000000, "rate": 11, "tenure": 60, "emi": 1291667, "start": "2024-01-15", "out": 38000000},
    {"type": "External", "lender": "City Bank", "principal": 30000000, "rate": 12, "tenure": 48, "emi": 925000, "start": "2024-06-01", "out": 21000000},
    {"type": "Internal", "lender": "Corporate Fund", "principal": 15000000, "rate": 9, "tenure": 24, "emi": 737500, "start": "2025-01-10", "out": 9000000},
    {"type": "External", "lender": "IDLC Finance", "principal": 25000000, "rate": 13.5, "tenure": 36, "emi": 975694, "start": "2025-05-20", "out": 19000000},
]


def seed_sweep2():
    n = {"handover": 0, "variations": 0, "labor": 0, "investments": 0, "loans": 0}
    for h in HANDOVER:
        if frappe.db.get_value("REM Handover", {"unit": h["unit"]}, "name"):
            continue
        d = frappe.new_doc("REM Handover")
        d.unit = h["unit"]; d.customer = h["customer"]; d.project = h["project"]
        d.unit_type = h["type"]; d.status = h["status"]; d.handover_date = h["date"]
        d.snags = h["snags"]; d.pos_date = h["posDate"] or None
        d.total_value = h["tv"]; d.paid_amount = h["paid"]
        d.remarks = h["remarks"]; d.assigned_to = h["assigned"]
        d.save(ignore_permissions=True)
        n["handover"] += 1
    frappe.db.commit()
    for v in VARIATIONS:
        if frappe.db.get_value("REM Variation Order", {"title": v["title"]}, "name"):
            continue
        d = frappe.new_doc("REM Variation Order")
        d.project = v["project"]; d.title = v["title"]; d.status = v["status"]
        d.impact = v["impact"]; d.originator = v["originator"]
        d.vo_date = v["date"]; d.schedule = v["schedule"]
        d.save(ignore_permissions=True)
        n["variations"] += 1
    frappe.db.commit()
    for w in LABOR:
        if frappe.db.get_value("REM Labor", {"worker_name": w["name"]}, "name"):
            continue
        d = frappe.new_doc("REM Labor")
        d.worker_name = w["name"]; d.category = w["cat"]; d.site = w["site"]
        d.phone = w["phone"]; d.daily_wage = w["sal"]; d.rating = w["rating"]
        d.join_date = w["join"]
        d.save(ignore_permissions=True)
        n["labor"] += 1
    frappe.db.commit()
    for inv in INVESTMENTS:
        if frappe.db.get_value("REM Investment", {"investor_name": inv["inv"]}, "name"):
            continue
        d = frappe.new_doc("REM Investment")
        d.investor_name = inv["inv"]; d.project = inv["proj"]; d.amount = inv["amt"]
        d.interest_rate = inv["rate"]; d.start_date = inv["start"]
        d.tenure_months = inv["tenure"]; d.schedule = inv["sched"]
        d.save(ignore_permissions=True)
        n["investments"] += 1
    frappe.db.commit()
    for ln in LOANS:
        if frappe.db.get_value("REM Loan", {"lender": ln["lender"]}, "name"):
            continue
        d = frappe.new_doc("REM Loan")
        d.loan_type = ln["type"]; d.lender = ln["lender"]; d.principal = ln["principal"]
        d.interest_rate = ln["rate"]; d.tenure_months = ln["tenure"]; d.emi = ln["emi"]
        d.start_date = ln["start"]; d.outstanding = ln["out"]
        d.save(ignore_permissions=True)
        n["loans"] += 1
    frappe.db.commit()
    print(json.dumps(n))
