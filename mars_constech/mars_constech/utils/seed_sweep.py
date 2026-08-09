import frappe, json

ASSETS = [
    {"ref": "FA-001", "name": "Jolshiri Abason Land", "cat": "Land & Building", "date": "2024-01-15", "cost": 250000000, "loc": "Jolshiri"},
    {"ref": "FA-002", "name": "Head Office Building", "cat": "Land & Building", "date": "2024-03-01", "cost": 80000000, "loc": "Gulshan"},
    {"ref": "FA-003", "name": "Toyota Hiace (Site)", "cat": "Vehicles", "date": "2024-05-10", "cost": 5500000, "loc": "Muktodhara Site"},
    {"ref": "FA-004", "name": "Pickup Truck (Muktodhara)", "cat": "Vehicles", "date": "2024-07-01", "cost": 3200000, "loc": "Muktodhara Site"},
    {"ref": "FA-005", "name": "Tower Crane", "cat": "Equipment", "date": "2024-06-20", "cost": 15000000, "loc": "Jolshiri"},
    {"ref": "FA-006", "name": "Concrete Mixer (2 units)", "cat": "Equipment", "date": "2024-08-01", "cost": 2400000, "loc": "Muktodhara"},
    {"ref": "FA-007", "name": "Office Furniture & Fittings", "cat": "Furniture", "date": "2024-02-01", "cost": 1200000, "loc": "Head Office"},
    {"ref": "FA-008", "name": "IT Equipment & Computers", "cat": "IT & Software", "date": "2024-04-01", "cost": 1800000, "loc": "Head Office"},
]

TICKETS = [
    {"subject": "Water seepage in flat 4B — Jolshiri Tower A", "customer": "Dr. Rubina Ali", "status": "Open", "priority": "High", "type": "Defect", "desc": "Reported water seepage in bathroom wall. Site team to inspect."},
    {"subject": "Car parking allocation query — Plot 17", "customer": "Md. Taher Uddin", "status": "Open", "priority": "Medium", "type": "Enquiry", "desc": "Customer asking about parking slot allocation for plot 17."},
    {"subject": "Mutation document status", "customer": "Kamrul Hasan", "status": "Resolved", "priority": "Low", "type": "Documentation", "desc": "Asked for update on land mutation; docs shared via portal.", "resolution": "Documents shared via customer portal on 2026-07-30."},
    {"subject": "Brick quality concern — Phase 2", "customer": "Fatima Begum", "status": "Open", "priority": "High", "type": "Quality", "desc": "Customer raised concern about brick quality at Phase 2 site visit."},
]

APPROVALS = [
    {"type": "Expense", "ref": "EXP-2026-014", "title": "Site office rent — Muktodhara", "by": "Rofiqul Islam", "dept": "Construction", "amount": 250000, "date": "2026-07-28", "priority": "High", "status": "Pending", "level": "Director", "notes": "Quarterly rent for site office."},
    {"type": "Vendor Payment", "ref": "PO-2026-041", "title": "Cement supplier advance (50%)", "by": "Shamim Reza", "dept": "Procurement", "amount": 1850000, "date": "2026-07-27", "priority": "High", "status": "Pending", "level": "Director", "notes": "Advance per PO terms."},
    {"type": "Expense", "ref": "EXP-2026-013", "title": "Marketing campaign — Jolshiri", "by": "Nazma Akhter", "dept": "Sales & Marketing", "amount": 450000, "date": "2026-07-25", "priority": "Medium", "status": "Approved", "level": "Director", "notes": "Digital + print campaign Q3."},
    {"type": "Contractor Bill", "ref": "RAB-2026-022", "title": "R.A. Bill #22 — Structure works", "by": "Tanvir Ahmed", "dept": "Construction", "amount": 5200000, "date": "2026-07-24", "priority": "High", "status": "Pending", "level": "Board", "notes": "Over budget 3.2% — board approval needed."},
    {"type": "Refund", "ref": "REF-2026-007", "title": "Customer refund — cancelled booking", "by": "Nazma Akhter", "dept": "Sales", "amount": 600000, "date": "2026-07-21", "priority": "Medium", "status": "Approved", "level": "Director", "notes": "80% refund after 10% deduction."},
]

BOQ = [
    {"item": "Earthwork Excavation", "cat": "Excavation", "proj": "Muktodhara Green Park", "qty": 2500, "unit": "CFT", "rate": 8, "status": "Approved"},
    {"item": "Brickwork 5\" Wall", "cat": "Brickwork", "proj": "Muktodhara Green Park", "qty": 15000, "unit": "Pcs", "rate": 12, "status": "Approved"},
    {"item": "Reinforced Concrete (1:1.5:3)", "cat": "Concrete", "proj": "Jolshiri Abason", "qty": 400, "unit": "CFT", "rate": 5500, "status": "Draft"},
    {"item": "Plastering 12mm", "cat": "Finishing", "proj": "Jolshiri Abason", "qty": 8500, "unit": "SFT", "rate": 35, "status": "Pending Review"},
    {"item": "Pile Foundation Bored Cast-in-situ", "cat": "Structural", "proj": "Jolshiri Abason", "qty": 45, "unit": "Pcs", "rate": 85000, "status": "Approved"},
    {"item": "Electrical Wiring & Cables", "cat": "MEP", "proj": "Jolshiri Abason", "qty": 2500, "unit": "RFT", "rate": 120, "status": "Approved"},
]


def _company():
    return frappe.db.get_value("Company", {}, "name") or "Mars Constact"


def _asset_category(name):
    c = frappe.db.get_value("Asset Category", {"asset_category_name": name}, "name")
    if c:
        return c
    d = frappe.new_doc("Asset Category")
    d.asset_category_name = name
    d.flags.ignore_mandatory = True
    d.save(ignore_permissions=True)
    return d.name


def _location(name):
    l = frappe.db.get_value("Location", {"location_name": name}, "name")
    if l:
        return l
    d = frappe.new_doc("Location")
    d.location_name = name
    d.flags.ignore_mandatory = True
    d.save(ignore_permissions=True)
    return d.name


def seed_sweep():
    # generic fixed-asset Item (Asset.item_code is mandatory)
    fa_item = frappe.db.get_value("Item", {"item_name": "Fixed Asset"}, "name")
    if not fa_item:
        d = frappe.new_doc("Item")
        d.item_code = "REM-FIXED-ASSET"
        d.item_name = "Fixed Asset"
        d.item_group = "All Item Groups"
        d.is_stock_item = 0
        d.is_fixed_asset = 1
        d.asset_category = _asset_category("Equipment")
        d.flags.ignore_mandatory = True
        d.save(ignore_permissions=True)
        fa_item = d.name
    # assets
    na = 0
    for a in ASSETS:
        if frappe.db.get_value("Asset", {"custom_rem_ref": a["ref"]}, "name"):
            continue
        d = frappe.new_doc("Asset")
        d.custom_rem_ref = a["ref"]
        d.item_code = fa_item
        d.item_name = a["name"][:140]
        d.asset_name = a["name"][:140]
        d.is_existing_asset = 1
        d.company = _company()
        d.calculate_depreciation = 0
        d.gross_purchase_amount = a["cost"]
        d.purchase_date = a["date"]
        d.available_for_use_date = a["date"]
        d.asset_category = _asset_category(a["cat"])
        d.location = _location(a["loc"])
        d.status = "Submitted"
        d.flags.ignore_mandatory = True
        d.save(ignore_permissions=True)
        na += 1
    # tickets (create Issue Types first — Issue.issue_type is a mandatory link)
    nt = 0
    it_map = {}
    for itname in ("Defect", "Enquiry", "Documentation", "Quality", "Service Request", "Complaint"):
        nm = frappe.db.get_value("Issue Type", {"name": itname}, "name")
        if not nm:
            d = frappe.new_doc("Issue Type")
            d.name = itname
            d.description = itname
            d.flags.ignore_mandatory = True
            d.save(ignore_permissions=True)
            nm = d.name
        it_map[itname] = nm
    for t in TICKETS:
        if frappe.db.get_value("Issue", {"subject": t["subject"]}, "name"):
            continue
        d = frappe.new_doc("Issue")
        d.subject = t["subject"]
        d.customer_name = t["customer"]
        d.status = t["status"]
        d.priority = t["priority"]
        d.issue_type = it_map.get(t["type"], it_map["Service Request"])
        d.description = t["desc"]
        if t.get("resolution"):
            d.resolution_details = t["resolution"]
        d.opening_date = frappe.utils.today()
        d.flags.ignore_mandatory = True
        d.save(ignore_permissions=True)
        nt += 1
    frappe.db.commit()
    # approvals
    nap = 0
    for a in APPROVALS:
        if frappe.db.get_value("REM Approval", {"reference": a["ref"]}, "name"):
            continue
        d = frappe.new_doc("REM Approval")
        d.approval_type = a["type"]
        d.reference = a["ref"]
        d.title = a["title"]
        d.requested_by = a["by"]
        d.department = a["dept"]
        d.amount = a["amount"]
        d.approval_date = a["date"]
        d.priority = a["priority"]
        d.status = a["status"]
        d.level = a["level"]
        d.notes = a["notes"]
        d.save(ignore_permissions=True)
        nap += 1
    frappe.db.commit()
    # boq
    nb = 0
    for b in BOQ:
        if frappe.db.get_value("REM BOQ", {"item": b["item"]}, "name"):
            continue
        d = frappe.new_doc("REM BOQ")
        d.item = b["item"]
        d.category = b["cat"]
        d.project = b["proj"]
        d.qty = b["qty"]
        d.unit = b["unit"]
        d.rate = b["rate"]
        d.status = b["status"]
        d.updated = frappe.utils.today()
        d.save(ignore_permissions=True)
        nb += 1
    frappe.db.commit()
    print(json.dumps({"assets": na, "tickets": nt, "approvals": nap, "boq": nb}))
