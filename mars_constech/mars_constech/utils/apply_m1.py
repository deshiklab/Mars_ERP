import frappe, json

def apply_m1():
    """M1: enable 2FA, shorten sessions, tighten login attempts."""
    ss = frappe.get_single("System Settings")
    ss.enable_two_factor_auth = 1
    ss.two_factor_method = "OTP App"
    ss.session_expiry = "08:00"
    ss.allow_consecutive_login_attempts = 3
    ss.allow_login_attempts = 3
    ss.save(ignore_permissions=True)
    frappe.db.commit()
    print(json.dumps({
        "two_factor": ss.enable_two_factor_auth,
        "method": ss.two_factor_method,
        "session_expiry": ss.session_expiry,
        "login_attempts": ss.allow_consecutive_login_attempts,
    }))
