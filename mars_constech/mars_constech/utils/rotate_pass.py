import frappe, json, secrets, string

def rotate_passwords():
    """Rotate all system + demo user passwords to strong random values."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    def gen():
        return "".join(secrets.choice(alphabet) for _ in range(16))
    users = ["Administrator", "manager@mars.com", "agent@mars.com",
             "customer@mars.com", "rubina@mars.com"]
    out = {}
    for u in users:
        if not frappe.db.exists("User", u):
            continue
        new = gen()
        user = frappe.get_doc("User", u)
        user.new_password = new
        user.save(ignore_permissions=True)
        frappe.db.commit()
        out[u] = new
    print(json.dumps(out))

def set_2fa_off():
    """Ensure 2FA flag currently off (M1 will turn it on deliberately later)."""
    frappe.db.set_value("System Settings", "System Settings", "enable_two_factor_auth", 0)
    frappe.db.commit()
    print("2fa baseline off")
