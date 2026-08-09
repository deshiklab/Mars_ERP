import frappe, json
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def mk_stock_cf():
    fields = {
        "Item": [
            {"fieldname": "custom_rem_ref", "label": "REM Ref", "fieldtype": "Data"},
            {"fieldname": "custom_rem_site", "label": "REM Site", "fieldtype": "Data"},
            {"fieldname": "custom_rem_category", "label": "REM Category", "fieldtype": "Data"},
            {"fieldname": "custom_reorder_level", "label": "Reorder Level", "fieldtype": "Float", "default": "0"},
            {"fieldname": "custom_rem_last_received", "label": "REM Last Received", "fieldtype": "Data"},
        ],
        "Purchase Order": [
            {"fieldname": "custom_rem_ref", "label": "REM Ref", "fieldtype": "Data"},
            {"fieldname": "custom_rem_site", "label": "REM Site", "fieldtype": "Data"},
            {"fieldname": "custom_rem_category", "label": "REM Category", "fieldtype": "Data"},
            {"fieldname": "custom_rem_approved_by", "label": "REM Approved By", "fieldtype": "Data"},
        ],
    }
    create_custom_fields(fields, ignore_validate=True)
    frappe.db.commit()
    print("stock custom fields created")
