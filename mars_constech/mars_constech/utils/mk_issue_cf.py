import frappe, json
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def mk_issue_cf():
    fields = {
        "Issue": [
            {"fieldname": "custom_rem_project", "fieldtype": "Data", "label": "Project"},
            {"fieldname": "custom_rem_unit", "fieldtype": "Data", "label": "Unit"},
            {"fieldname": "custom_rem_assigned", "fieldtype": "Data", "label": "Assigned To"},
            {"fieldname": "custom_rem_sla_days", "fieldtype": "Int", "label": "SLA (days)", "default": 0},
            {"fieldname": "custom_rem_resolved_date", "fieldtype": "Date", "label": "Resolved Date"},
            {"fieldname": "custom_rem_satisfaction", "fieldtype": "Int", "label": "Satisfaction (1-5)"},
            {"fieldname": "custom_rem_owner", "fieldtype": "Data", "label": "Owner"},
        ]
    }
    create_custom_fields(fields)
    print("issue custom fields created")
