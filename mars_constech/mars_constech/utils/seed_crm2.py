import frappe, json
from frappe.utils import now_datetime, add_to_date

# enrich remaining real leads with follow-up + last-contact so the
# improved pipeline shows varied relative times
EXTRA = [
    ("syed@example.com", "High", 0, 5, "Pending", "Bank Loan", "Flat"),
    ("shamim@example.com", "Medium", 2, 26, "Up to Date", "Construction Link", "Land"),
    ("jahanara@example.com", "Low", None, 72, "Up to Date", "Full Payment", "Flat"),
    ("taher@example.com", "High", 1, 8, "Pending", "Construction Link", "Plot"),
    ("salahuddin@example.com", "Medium", None, 200, "Up to Date", "Bank Loan", "Flat"),
]


def enrich_more():
    n = 0
    for email, prio, fup_days, last_h, payst, plan, ftype in EXTRA:
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
        n += 1
    frappe.db.commit()
    print(json.dumps({"leads": n}))
