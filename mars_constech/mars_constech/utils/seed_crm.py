import frappe, json

BROKERS = [
    {"name": "Md. Shahidul Haque", "phone": "+880 1711 888800", "tier": "Platinum", "pct": 5, "region": "Purbachal", "leads": 24, "deals": 12, "paid": "৳18.5L", "joined": "Jan 2024"},
    {"name": "Nurul Islam", "phone": "+880 1812 777700", "tier": "Gold", "pct": 4, "region": "Rupganj", "leads": 18, "deals": 8, "paid": "৳9.2L", "joined": "Mar 2024"},
    {"name": "Abdur Rahim Khan", "phone": "+880 1913 666600", "tier": "Gold", "pct": 4, "region": "Bashundhara", "leads": 15, "deals": 6, "paid": "৳7.8L", "joined": "Jun 2024"},
    {"name": "Shamima Akhter", "phone": "+880 1714 555500", "tier": "Silver", "pct": 3, "region": "Mirpur", "leads": 10, "deals": 4, "paid": "৳3.5L", "joined": "Aug 2024"},
    {"name": "Md. Farid Uddin", "phone": "+880 1815 444400", "tier": "Silver", "pct": 3, "region": "Uttara", "leads": 8, "deals": 3, "paid": "৳2.1L", "joined": "Oct 2024"},
    {"name": "Hasan Mahmud", "phone": "+880 1916 333300", "tier": "Platinum", "pct": 5, "region": "Savar", "leads": 30, "deals": 15, "paid": "৳22.0L", "joined": "Jan 2024"},
]

COMPLAINTS = [
    {"client": "Dr. Rubina Ali", "project": "Jolshiri Abason", "unit": "Apt 4B", "type": "Quality", "desc": "Water leakage in master bathroom ceiling near pipe joint", "priority": "High", "status": "Open", "assigned": "Engr. Faruk", "filed": "2026-06-10", "sla": 7, "owner": "Iftekhar Ahmad"},
    {"client": "Kamrul Hasan", "project": "Jolshiri Abason", "unit": "Apt 9A", "type": "Maintenance", "desc": "Lift not working intermittently on 4th floor", "priority": "High", "status": "In Progress", "assigned": "Service Team", "filed": "2026-06-08", "sla": 3, "owner": "Sales Team A"},
    {"client": "Mrs. Jahanara Begum", "project": "Jolshiri Abason", "unit": "Apt 3C", "type": "Quality", "desc": "Cracks on drawing room wall near window frame", "priority": "Medium", "status": "Resolved", "assigned": "Engr. Faruk", "filed": "2026-05-28", "sla": 7, "resolved": "2026-06-05", "sat": 4, "owner": "Hasanul Banna"},
    {"client": "Tariqul Islam", "project": "Muktodhara Green Park", "unit": "Plot M-103", "type": "Legal", "desc": "Mutation deed registration delayed beyond promised 90 days", "priority": "High", "status": "Escalated", "assigned": "Legal Dept", "filed": "2026-05-15", "sla": 90, "owner": "MD Hasanul Banna"},
    {"client": "Shahidul Islam", "project": "Muktodhara Green Park", "unit": "Plot 15", "type": "Delayed Possession", "desc": "Possession delayed by 2 months from agreed handover date", "priority": "Critical", "status": "Escalated", "assigned": "Director", "filed": "2026-05-20", "sla": 45, "owner": "MD Hasanul Banna"},
]

LEAD_ENRICH = [
    # (email, priority, next_followup_days, last_contact_hours, payment_status, plan, flat_type)
    ("tariqul@example.com", "High", 0, 2, "Up to Date", "Construction Link", "Land"),
    ("rubina@example.com", "Medium", 1, 24, "Pending", "Construction Link", "Flat"),
    ("ahasan@example.com", "High", 0, 3, "Overdue", "Bank Loan", "Land"),
    ("kamrul@example.com", "Low", None, 120, "Up to Date", "Construction Link", "Flat"),
]


def seed_crm():
    n = {"brokers": 0, "complaints": 0, "leads": 0}
    for b in BROKERS:
        if frappe.db.get_value("REM Broker", {"broker_name": b["name"]}, "name"):
            continue
        d = frappe.new_doc("REM Broker")
        d.broker_name = b["name"]; d.phone = b["phone"]; d.tier = b["tier"]
        d.commission_pct = b["pct"]; d.region = b["region"]
        d.leads_referred = b["leads"]; d.deals_closed = b["deals"]
        d.commission_paid = b["paid"]; d.joined = b["joined"]
        d.save(ignore_permissions=True)
        n["brokers"] += 1
    frappe.db.commit()
    for c in COMPLAINTS:
        subj = c["desc"][:140]
        if frappe.db.get_value("Issue", {"subject": subj}, "name"):
            continue
        d = frappe.new_doc("Issue")
        d.subject = subj; d.description = c["desc"]
        d.customer_name = c["client"]; d.issue_type = "Complaint"
        d.priority = {"Critical": "High"}.get(c["priority"], c["priority"])
        d.status = {"In Progress": "Replied", "Escalated": "Open"}.get(c["status"], c["status"])
        d.opening_date = c["filed"]
        d.custom_rem_project = c["project"]; d.custom_rem_unit = c["unit"]
        d.custom_rem_assigned = c["assigned"]; d.custom_rem_sla_days = c["sla"]
        if c.get("resolved"): d.custom_rem_resolved_date = c["resolved"]
        if c.get("sat") is not None: d.custom_rem_satisfaction = c["sat"]
        d.custom_rem_owner = c["owner"]
        d.flags.ignore_mandatory = True
        d.save(ignore_permissions=True)
        n["complaints"] += 1
    frappe.db.commit()
    # enrich existing leads
    from frappe.utils import now_datetime, add_days, add_to_date
    for email, prio, fup_days, last_h, payst, plan, ftype in LEAD_ENRICH:
        name = frappe.db.get_value("Lead", {"email_id": email}, "name")
        if not name:
            continue
        doc = frappe.get_doc("Lead", name)
        doc.custom_rem_priority = prio
        if fup_days is not None:
            doc.custom_rem_next_follow_up = add_to_date(now_datetime(), days=fup_days, hours=15)
        if last_h is not None:
            doc.custom_rem_last_contact = add_to_date(now_datetime(), hours=-last_h)
        doc.custom_rem_payment_status = payst
        doc.custom_rem_payment_plan = plan
        doc.custom_rem_flat_type = ftype
        doc.save(ignore_permissions=True)
        n["leads"] += 1
    frappe.db.commit()
    print(json.dumps(n))
