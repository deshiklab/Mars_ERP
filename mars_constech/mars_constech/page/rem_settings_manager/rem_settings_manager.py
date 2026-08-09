# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_settings():
    """Current REM Settings (server-backed PWA connection config)."""
    doc = frappe.get_single("REM Settings")
    return {
        "pwa_version": doc.pwa_version or "",
        "api_base_override": doc.api_base_override or "",
        "auto_connect": bool(doc.auto_connect),
        "push_on_save": bool(doc.push_on_save),
        "auto_heal": bool(doc.auto_heal),
        "live_land": bool(doc.live_land),
        "session_expiry_hint": doc.session_expiry_hint or "",
        "last_connected_user": doc.last_connected_user or "",
        "last_sync_time": str(doc.last_sync_time or "")[:19],
    }


@frappe.whitelist()
def save_settings(settings=None):
    """Persist REM Settings from the desk page (same guard as the PWA endpoint)."""
    if not settings or not isinstance(settings, dict):
        frappe.throw(_("settings must be an object"), frappe.ValidationError)
    allowed = {"pwa_version", "api_base_override", "auto_connect", "push_on_save",
               "auto_heal", "live_land"}
    doc = frappe.get_single("REM Settings")
    for k, v in settings.items():
        if k not in allowed:
            continue
        if k in ("auto_connect", "push_on_save", "auto_heal", "live_land"):
            doc.db_set(k, 1 if v else 0)
        else:
            doc.db_set(k, str(v or ""))
    frappe.db.commit()
    return {"ok": True, "settings": get_settings()}
