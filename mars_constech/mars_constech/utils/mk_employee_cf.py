import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def mk_employee_cf():
    fields = {
        "Employee": [
            {"fieldname": "custom_rem_ref", "label": "REM Ref", "fieldtype": "Data"},
            {"fieldname": "custom_contract_type", "label": "Contract Type", "fieldtype": "Data"},
            {"fieldname": "custom_contract_start", "label": "Contract Start", "fieldtype": "Date"},
            {"fieldname": "custom_contract_end", "label": "Contract End", "fieldtype": "Date"},
            {"fieldname": "custom_notice_days", "label": "Notice Days", "fieldtype": "Int", "default": "30"},
            {"fieldname": "custom_salary_clause", "label": "Salary Clause", "fieldtype": "Small Text"},
            {"fieldname": "custom_insurance_provider", "label": "Insurance Provider", "fieldtype": "Data"},
            {"fieldname": "custom_insurance_policy", "label": "Policy No", "fieldtype": "Data"},
            {"fieldname": "custom_insurance_coverage", "label": "Coverage", "fieldtype": "Currency"},
            {"fieldname": "custom_insurance_expiry", "label": "Insurance Expiry", "fieldtype": "Date"},
        ]
    }
    create_custom_fields(fields, ignore_validate=True)
    frappe.db.commit()
    print("employee custom fields created")
