#!/usr/bin/env python3
"""Add custom_rem_ref to Journal Entry for dedupe."""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

create_custom_fields({
    "Journal Entry": [
        {
            "fieldname": "custom_rem_ref",
            "fieldtype": "Data",
            "label": "REM Ref",
            "insert_after": "title",
            "description": "PWA-side journal id (JNL-xxx) for dedupe",
        },
    ],
}, ignore_validate=True)
frappe.db.commit()

rows = frappe.get_all("Custom Field", filters={"dt": "Journal Entry", "fieldname": "custom_rem_ref"}, fields=["fieldname"])
print("JE custom fields:", [r.fieldname for r in rows])
