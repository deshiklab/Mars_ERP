import frappe, json, pyotp
from frappe.twofactor import get_otpsecret_for_, two_factor_is_enabled

def finalize_2fa():
    """Mark the OTP setup complete for all users (skip the email-setup path):
    setting <user>_otplogin=1 makes get_verification_obj use
    process_2fa_for_otp_app (QR/secret) instead of process_2fa_for_email."""
    out = {}
    for u in ("manager@mars.com", "agent@mars.com", "customer@mars.com", "rubina@mars.com"):
        secret = get_otpsecret_for_(u)
        frappe.db.set_default(u + "_otplogin", "1")
        out[u] = {"secret": secret, "otpauth": pyotp.TOTP(secret).provisioning_uri(name=u, issuer_name="MARS ERP")}
    frappe.db.commit()
    # confirm
    out["_manager_2fa_active"] = bool(two_factor_is_enabled("manager@mars.com"))
    print(json.dumps(out))
