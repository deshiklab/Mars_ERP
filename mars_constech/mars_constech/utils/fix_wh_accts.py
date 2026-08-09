import frappe, json

def fix_warehouse_accounts():
    company = frappe.db.get_value("Company", {}, "name") or "Mars Constact"
    acct = frappe.db.get_value("Account", {"account_name": "Stock In Hand", "company": company}, "name")
    if not acct:
        acct = frappe.db.sql_list("SELECT name FROM `tabAccount` WHERE account_type='Stock' AND is_group=0 AND company=%s LIMIT 1", company)
        acct = acct[0] if acct else ""
    fixed = 0
    for wh in frappe.get_all("Warehouse", fields=["name", "account"]):
        if wh.account != acct:
            frappe.db.set_value("Warehouse", wh.name, "account", acct)
            fixed += 1
    frappe.db.set_value("Company", company, "default_inventory_account", acct)
    frappe.db.commit()
    print(json.dumps({"account": acct, "warehouses_fixed": fixed}))
