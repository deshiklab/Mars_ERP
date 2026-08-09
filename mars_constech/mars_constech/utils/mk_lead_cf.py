import frappe, json
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def mk_lead_cf():
    fields = {
        "Lead": [
            {"fieldname": "custom_rem_priority", "fieldtype": "Select", "label": "Priority",
             "options": "Low\nMedium\nHigh", "default": "Medium"},
            {"fieldname": "custom_rem_next_follow_up", "fieldtype": "Datetime", "label": "Next Follow-up"},
            {"fieldname": "custom_rem_last_contact", "fieldtype": "Datetime", "label": "Last Contact"},
            {"fieldname": "custom_rem_flat_type", "fieldtype": "Data", "label": "Flat Type"},
            {"fieldname": "custom_rem_facing_dir", "fieldtype": "Data", "label": "Facing Direction"},
            {"fieldname": "custom_rem_floor_pref", "fieldtype": "Data", "label": "Floor Preference"},
            {"fieldname": "custom_rem_size_sqft", "fieldtype": "Data", "label": "Size (sqft)"},
            {"fieldname": "custom_rem_payment_plan", "fieldtype": "Data", "label": "Payment Plan"},
            {"fieldname": "custom_rem_payment_status", "fieldtype": "Select", "label": "Payment Status",
             "options": "Up to Date\nPending\nOverdue", "default": "Up to Date"},
            {"fieldname": "custom_rem_broker_ref", "fieldtype": "Data", "label": "Broker Ref"},
            {"fieldname": "custom_rem_lead_score", "fieldtype": "Int", "label": "Lead Score",
             "read_only": 1, "default": 0},
            {"fieldname": "custom_rem_lead_activities", "fieldtype": "Table", "label": "Activity Log",
             "options": "REM Lead Activity"},
        ]
    }
    create_custom_fields(fields)
    print("lead custom fields created")
