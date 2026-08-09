import frappe, json, pyotp
from frappe.twofactor import get_otpsecret_for_, two_factor_is_enabled

def enable_manager_2fa():
    """Opt manager@mars.com into OTP 2FA; generate + expose its secret."""
    u = frappe.get_doc("User", "manager@mars.com")
    u.two_factor_auth = 1
    u.save(ignore_permissions=True)
    frappe.db.commit()
    secret = get_otpsecret_for_("manager@mars.com")  # generates + persists encrypted
    frappe.db.commit()
    print(json.dumps({
        "user": "manager@mars.com",
        "two_factor_auth": int(two_factor_is_enabled("manager@mars.com")),
        "otp_secret": secret,
        "otpauth": pyotp.TOTP(secret).provisioning_uri(name="manager@mars.com", issuer_name="MARS ERP"),
    }))
