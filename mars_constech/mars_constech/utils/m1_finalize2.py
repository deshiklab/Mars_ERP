import frappe, json, pyotp
from frappe.twofactor import get_otpsecret_for_

def finalize_2fa():
    """(Re)set OTP secrets + otplogin flag; verify rows persisted."""
    out = {}
    for u in ("manager@mars.com", "agent@mars.com", "customer@mars.com", "rubina@mars.com"):
        secret = get_otpsecret_for_(u)
        frappe.db.set_default(u + "_otplogin", "1")
        frappe.db.commit()
        # verify persisted
        v = frappe.db.get_default(u + "_otplogin")
        out[u] = {"secret_ok": bool(secret), "otplogin": v}
    frappe.db.commit()
    print(json.dumps(out))
