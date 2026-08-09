import frappe, json
from frappe.twofactor import get_otpsecret_for_

def dump_secrets():
    out = {}
    for u in ("agent@mars.com", "manager@mars.com"):
        out[u] = get_otpsecret_for_(u)
    frappe.db.commit()
    print(json.dumps(out))
