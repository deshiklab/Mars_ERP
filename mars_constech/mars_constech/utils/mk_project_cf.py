#!/usr/bin/env python3
"""Create custom fields on Project + Task for the REM bridge."""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

fields = {
    "Project": [
        {
            "fieldname": "custom_rem_ref",
            "fieldtype": "Data",
            "label": "REM Ref",
            "insert_after": "project_name",
            "description": "PWA-side project id (P-xxx)",
        },
        {
            "fieldname": "custom_rem_type",
            "fieldtype": "Select",
            "label": "REM Type",
            "options": "\nland\nflat\nmixed",
            "insert_after": "custom_rem_ref",
        },
        {
            "fieldname": "custom_rem_progress",
            "fieldtype": "Percent",
            "label": "REM Progress",
            "insert_after": "custom_rem_type",
        },
        {
            "fieldname": "custom_rem_plots",
            "fieldtype": "Int",
            "label": "REM Plots",
            "insert_after": "custom_rem_progress",
        },
        {
            "fieldname": "custom_rem_phase",
            "fieldtype": "Data",
            "label": "REM Phase",
            "insert_after": "custom_rem_plots",
        },
        {
            "fieldname": "custom_rem_budget",
            "fieldtype": "Currency",
            "label": "REM Budget",
            "insert_after": "custom_rem_phase",
        },
        {
            "fieldname": "custom_rem_la_ref",
            "fieldtype": "Data",
            "label": "REM Land Acquisition Ref",
            "insert_after": "custom_rem_budget",
            "description": "Linked Land Acquisition name (from merge-to-Project)",
        },
    ],
    "Task": [
        {
            "fieldname": "custom_rem_ref",
            "fieldtype": "Data",
            "label": "REM Ref",
            "insert_after": "subject",
        },
        {
            "fieldname": "custom_rem_priority",
            "fieldtype": "Select",
            "label": "REM Priority",
            "options": "\nLow\nMedium\nHigh\nUrgent",
            "default": "Medium",
            "insert_after": "custom_rem_ref",
        },
    ],
}

create_custom_fields(fields, ignore_validate=True)
frappe.db.commit()

for dt in ("Project", "Task"):
    rows = frappe.get_all("Custom Field", filters={"dt": dt, "fieldname": ["like", "custom_rem%"]}, fields=["fieldname"])
    print(dt, "custom fields:", [r.fieldname for r in rows])
