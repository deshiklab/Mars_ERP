#!/usr/bin/env python3
"""Create REM custom fields on Lead directly (same pattern as mk-acqref.py)."""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

fields = {
    "Lead": [
        {
            "fieldname": "custom_rem_status",
            "fieldtype": "Select",
            "label": "REM Status",
            "options": "\nNew Inquiry\nSite Visit\nNegotiation\nBooking\nDownpayment\nInstallments\nConverted\nLost",
            "default": "New Inquiry",
            "insert_after": "status",
            "description": "REM PWA sales funnel status",
        },
        {
            "fieldname": "custom_rem_ref",
            "fieldtype": "Data",
            "label": "REM Ref",
            "insert_after": "custom_rem_status",
            "description": "PWA-side lead id (LD-xxx) for dedupe",
        },
        {
            "fieldname": "custom_rem_value",
            "fieldtype": "Currency",
            "label": "REM Expected Value",
            "insert_after": "custom_rem_ref",
            "description": "Expected deal value in BDT",
        },
        {
            "fieldname": "custom_rem_property",
            "fieldtype": "Data",
            "label": "REM Property Interest",
            "insert_after": "custom_rem_value",
            "description": "Project / unit the lead is interested in",
        },
    ]
}

create_custom_fields(fields, ignore_validate=True)
frappe.db.commit()

rows = frappe.get_all("Custom Field", filters={"dt": "Lead", "fieldname": ["like", "custom_rem%"]}, fields=["fieldname", "fieldtype"])
print("Lead custom fields:", [(r.fieldname, r.fieldtype) for r in rows])
