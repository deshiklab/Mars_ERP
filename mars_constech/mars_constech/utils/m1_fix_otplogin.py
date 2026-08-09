import frappe, json
from frappe.twofactor import set_default as tf_set_default
from frappe.twofactor import get_default as tf_get_default

def fix_otplogin():
    """Write otplogin defaults with the SAME parent twofactor.py reads (__2fa)."""
    out = {}
    for u in ("manager@mars.com", "agent@mars.com", "customer@mars.com", "rubina@mars.com"):
        tf_set_default(u + "_otplogin", "1")
        frappe.db.commit()
        out[u] = tf_get_default(u + "_otplogin")
    frappe.db.commit()
    print(json.dumps(out))
