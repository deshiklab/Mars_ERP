#!/usr/bin/env python3
"""Create custom fields on Item for the Plots & Units bridge."""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

fields = {
    "Item": [
        {
            "fieldname": "custom_rem_type",
            "fieldtype": "Select",
            "label": "REM Unit Type",
            "options": "\n3 Katha\n5 Katha\n10 Katha\nFlat - 2BHK\nFlat - 3BHK\nCommercial",
            "insert_after": "item_code",
        },
        {
            "fieldname": "custom_rem_block",
            "fieldtype": "Data",
            "label": "REM Block",
            "insert_after": "custom_rem_type",
        },
        {
            "fieldname": "custom_rem_status",
            "fieldtype": "Select",
            "label": "REM Status",
            "options": "\navailable\nreserved\nsold\nnot_acquired",
            "default": "available",
            "insert_after": "custom_rem_block",
        },
        {
            "fieldname": "custom_rem_katha",
            "fieldtype": "Data",
            "label": "REM Katha",
            "insert_after": "custom_rem_status",
            "description": "e.g. 3, 5, 10",
        },
        {
            "fieldname": "custom_rem_price",
            "fieldtype": "Currency",
            "label": "REM Price (BDT)",
            "insert_after": "custom_rem_katha",
        },
        {
            "fieldname": "custom_rem_booking_ref",
            "fieldtype": "Data",
            "label": "REM Booking Ref",
            "insert_after": "custom_rem_price",
            "description": "Linked booking id (BKG-xxx) when sold/reserved",
        },
    ],
}

create_custom_fields(fields, ignore_validate=True)
frappe.db.commit()

rows = frappe.get_all("Custom Field", filters={"dt": "Item", "fieldname": ["like", "custom_rem%"]}, fields=["fieldname"])
print("Item custom fields:", [r.fieldname for r in rows])
