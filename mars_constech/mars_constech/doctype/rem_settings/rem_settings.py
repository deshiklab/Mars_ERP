# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class REMSettings(Document):
    """Single doctype holding PWA connection configuration.

    The PWA reads these settings via mars_constech.mars_constech.api.settings_get
    and writes them via settings_set — they are shared across all browsers/
    devices instead of living only in localStorage.
    """

    @staticmethod
    def get_settings_dict():
        doc = frappe.get_single("REM Settings")
        return {
            "pwa_version": doc.pwa_version or "2.0.0",
            "api_base_override": doc.api_base_override or "",
            "auto_connect": bool(doc.auto_connect),
            "push_on_save": bool(doc.push_on_save),
            "auto_heal": bool(doc.auto_heal),
            "live_land": bool(doc.live_land),
            "session_expiry": doc.session_expiry_hint or "",
            "last_connected_user": doc.last_connected_user or "",
            "last_sync_time": doc.last_sync_time or "",
        }
