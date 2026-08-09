import frappe, json
from datetime import date

# Mirror of the PWA mockInventory — becomes real stock Items with initial stock
INVENTORY = [
    {"id": 1, "site": "Muktodhara", "item": "BSRM Steel 500W", "category": "Construction Material", "qty": 45, "unit": "Tons", "price": 410000, "reorder": 20, "supplier": "BSRM Steels Ltd.", "last": "Oct 23, 2024"},
    {"id": 2, "site": "Muktodhara", "item": "Shah Cement", "category": "Construction Material", "qty": 150, "unit": "Bags", "price": 550, "reorder": 500, "supplier": "Shah Cement Ltd.", "last": "Oct 25, 2024"},
    {"id": 3, "site": "Jolshiri", "item": "Bricks (Class A)", "category": "Construction Material", "qty": 12000, "unit": "Pcs", "price": 12, "reorder": 15000, "supplier": "Local Sand Suppliers", "last": "Oct 18, 2024"},
    {"id": 4, "site": "Jolshiri", "item": "Sylhet Sand", "category": "Construction Material", "qty": 800, "unit": "CFT", "price": 60, "reorder": 300, "supplier": "Local Sand Suppliers", "last": "Oct 15, 2024"},
    {"id": 5, "site": "Corporate", "item": "Office Furniture", "category": "Admin", "qty": 25, "unit": "Sets", "price": 15000, "reorder": 5, "supplier": "RFL Building Products", "last": "Sep 10, 2024"},
    {"id": 6, "site": "Muktodhara", "item": "PVC Pipes 4 inch", "category": "Plumbing", "qty": 200, "unit": "Pcs", "price": 850, "reorder": 50, "supplier": "RFL Building Products", "last": "Oct 05, 2024"},
    {"id": 7, "site": "Jolshiri", "item": "Electrical Cable (6mm)", "category": "Electrical", "qty": 500, "unit": "Meters", "price": 120, "reorder": 400, "supplier": "Delta Electricals", "last": "Sep 28, 2024"},
    {"id": 8, "site": "Muktodhara", "item": "Ceramic Tiles (2x2)", "category": "Finishes", "qty": 350, "unit": "Boxes", "price": 950, "reorder": 100, "supplier": "RFL Building Products", "last": "Oct 10, 2024"},
    {"id": 9, "site": "Jolshiri", "item": "Safety Helmets", "category": "Safety", "qty": 45, "unit": "Pcs", "price": 250, "reorder": 60, "supplier": "Delta Electricals", "last": "Sep 20, 2024"},
    {"id": 10, "site": "Muktodhara", "item": "Paint (Asian 10L)", "category": "Finishes", "qty": 60, "unit": "Buckets", "price": 3200, "reorder": 20, "supplier": "RFL Building Products", "last": "Oct 08, 2024"},
]

_PO_STATUS = {"Pending Approval": "Draft", "Approved": "To Receive and Bill",
              "Delivered": "Delivered", "Completed": "Completed", "Cancelled": "Cancelled"}

POS = [
    {"ref": "PO-24-089", "vendor": "Shah Cement Ltd.", "site": "Muktodhara", "item": "Cement (1000 Bags)", "qty": 1000, "amount": 550000, "due": "2024-11-10", "status": "Pending Approval", "category": "Material", "approved_by": ""},
    {"ref": "PO-24-088", "vendor": "BSRM Steels Ltd.", "site": "Jolshiri", "item": "500W Steel (20 Tons)", "qty": 20, "amount": 1840000, "due": "2024-11-05", "status": "Approved", "category": "Material", "approved_by": "MD Hasanul Banna"},
    {"ref": "PO-24-087", "vendor": "RFL Building Products", "site": "Muktodhara", "item": "Ceramic Tiles (100 Boxes)", "qty": 100, "amount": 95000, "due": "2024-11-15", "status": "Approved", "category": "Finishes", "approved_by": "Iftekhar Ahmad"},
]


def _company():
    return frappe.db.get_value("Company", {}, "name") or "Mars Constact"


def _uom(unit):
    m = {"Tons": "Tonne", "Bags": "Nos", "Pcs": "Nos", "CFT": "Nos", "Sets": "Set",
         "Meters": "Meter", "Boxes": "Box", "Buckets": "Litre"}
    return m.get(unit, "Nos")


def _item_group():
    g = frappe.db.get_value("Item Group", "Products", "name")
    if g:
        return g
    d = frappe.new_doc("Item Group")
    d.item_group_name = "Products"
    d.parent_item_group = "All Item Groups"
    d.flags.ignore_mandatory = True
    d.save(ignore_permissions=True)
    return d.name


def _warehouse(site):
    name = site + " - MC"
    w = frappe.db.get_value("Warehouse", {"warehouse_name": site}, "name")
    if w:
        return w
    d = frappe.new_doc("Warehouse")
    d.warehouse_name = site
    d.company = _company()
    acct = frappe.db.get_value("Account", {"account_name": "Stock In Hand", "company": _company()}, "name")
    if acct:
        d.account = acct
    d.flags.ignore_mandatory = True
    d.save(ignore_permissions=True)
    return d.name


def _supplier(name):
    s = frappe.db.get_value("Supplier", {"supplier_name": name}, "name")
    if s:
        return s
    d = frappe.new_doc("Supplier")
    d.supplier_name = name
    d.supplier_group = "Local"
    d.flags.ignore_mandatory = True
    d.save(ignore_permissions=True)
    return d.name


def seed_stock():
    company = _company()
    ig = _item_group()
    item_map = {}
    # wipe any partially-created REM stock items so opening stock re-seeds cleanly
    for nm in frappe.db.sql_list("SELECT name FROM `tabItem` WHERE custom_rem_ref IS NOT NULL"):
        try:
            frappe.delete_doc("Item", nm, force=1, ignore_permissions=True)
        except Exception:
            pass
    frappe.db.commit()
    # ensure EVERY warehouse has the stock account (failed runs may have left some)
    _acct = frappe.db.get_value("Account", {"account_name": "Stock In Hand", "company": company}, "name")
    if _acct:
        for wh in frappe.get_all("Warehouse", fields=["name", "account"]):
            if wh.account != _acct:
                frappe.db.set_value("Warehouse", wh.name, "account", _acct)
        frappe.db.set_value("Company", company, "default_inventory_account", _acct)
    # create/update stock items
    for inv in INVENTORY:
        name = frappe.db.get_value("Item", {"custom_rem_ref": str(inv["id"])}, "name")
        if not name:
            d = frappe.new_doc("Item")
            d.item_code = "REM-" + inv["item"].replace(" ", "-").replace("(", "").replace(")", "")[:40]
            d.item_name = inv["item"]
            d.item_group = ig
            d.is_stock_item = 1
            d.is_purchase_item = 1
            d.stock_uom = _uom(inv["unit"])
            d.valuation_rate = inv["price"]
            d.standard_rate = inv["price"]
            # opening stock: ERPNext auto-creates the Material Receipt on insert
            d.opening_stock = inv["qty"]
            d.default_warehouse = _warehouse(inv["site"])
            d.flags.ignore_mandatory = True
            d.save(ignore_permissions=True)
        else:
            d = frappe.get_doc("Item", name)
        d.custom_rem_ref = str(inv["id"])
        d.custom_rem_site = inv["site"]
        d.custom_rem_category = inv["category"]
        d.custom_reorder_level = inv["reorder"]
        d.custom_rem_last_received = inv["last"]
        d.flags.ignore_mandatory = True
        d.save(ignore_permissions=True)
        item_map[inv["id"]] = d.name
    # (opening stock was set on item insert — ERPNext auto-created the receipts)
    # POs
    for po in POS:
        existing = frappe.db.get_value("Purchase Order", {"custom_rem_ref": po["ref"]}, "name")
        if existing:
            continue
        item_name = frappe.db.get_value("Item", {"custom_rem_ref": str([i for i in INVENTORY if i["item"].split(" (")[0] in po["item"] or po["item"].split(" (")[0] in i["item"]][0]["id"])}, "name") if any(po["item"].split(" (")[0] in i["item"] for i in INVENTORY) else None
        doc = frappe.new_doc("Purchase Order")
        doc.supplier = _supplier(po["vendor"])
        doc.company = company
        doc.transaction_date = po["due"]
        doc.schedule_date = po["due"]
        doc.status = _PO_STATUS.get(po["status"], "Draft")
        doc.custom_rem_ref = po["ref"]
        doc.custom_rem_site = po["site"]
        doc.custom_rem_category = po["category"]
        doc.custom_rem_approved_by = po["approved_by"]
        # find matching item (loose matcher: any shared word)
        matched = None
        for inv in INVENTORY:
            pw = [w for w in po["item"].lower().replace("(", " ").replace(")", " ").split() if len(w) > 2]
            iw = [w for w in inv["item"].lower().replace("(", " ").replace(")", " ").split() if len(w) > 2]
            if any(w in iw for w in pw) or any(w in pw for w in iw):
                matched = inv
                break
        if matched:
            doc.append("items", {
                "item_code": item_map[matched["id"]],
                "item_name": matched["item"],
                "schedule_date": po["due"],
                "qty": po["qty"],
                "stock_uom": _uom(matched["unit"]),
                "uom": _uom(matched["unit"]),
                "conversion_factor": 1,
                "rate": matched["price"],
                "price_list_rate": matched["price"],
                "base_rate": matched["price"],
                "base_price_list_rate": matched["price"],
                "amount": po["amount"],
                "base_amount": po["amount"],
            })
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)
    frappe.db.commit()
    print(json.dumps({
        "stock_items": frappe.db.count("Item", filters={"custom_rem_ref": ["is", "set"]}),
        "stock_entries": frappe.db.count("Stock Entry"),
        "bins": frappe.db.count("Bin"),
        "pos": frappe.db.count("Purchase Order"),
    }))
