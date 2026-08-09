#!/usr/bin/env python3
"""Custom fields on Supplier (contractor bridge) + Asset (equipment bridge)."""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

fields = {
    "Supplier": [
        {
            "fieldname": "custom_rem_type",
            "fieldtype": "Select",
            "label": "REM Contractor Type",
            "options": "\nCivil Works\nEarth Filling\nElectrical\nPlumbing\nMEP\nPainting\nRoofing\nGlass & Aluminum\nStructural\nFinishing\nLabour\nSupply",
            "insert_after": "supplier_name",
        },
        {
            "fieldname": "custom_rem_rating",
            "fieldtype": "Int",
            "label": "REM Rating",
            "insert_after": "custom_rem_type",
        },
        {
            "fieldname": "custom_rem_license",
            "fieldtype": "Data",
            "label": "REM License",
            "insert_after": "custom_rem_rating",
        },
        {
            "fieldname": "custom_rem_insurance",
            "fieldtype": "Data",
            "label": "REM Insurance",
            "insert_after": "custom_rem_license",
        },
        {
            "fieldname": "custom_rem_status",
            "fieldtype": "Select",
            "label": "REM Status",
            "options": "\nActive\nInactive",
            "default": "Active",
            "insert_after": "custom_rem_insurance",
        },
    ],
    "Asset": [
        {
            "fieldname": "custom_rem_ref",
            "fieldtype": "Data",
            "label": "REM Ref",
            "insert_after": "asset_name",
        },
        {
            "fieldname": "custom_rem_model",
            "fieldtype": "Data",
            "label": "REM Model",
            "insert_after": "custom_rem_ref",
        },
        {
            "fieldname": "custom_rem_type",
            "fieldtype": "Select",
            "label": "REM Type",
            "options": "\nHeavy\nLight\nTool\nVehicle",
            "insert_after": "custom_rem_model",
        },
        {
            "fieldname": "custom_rem_site",
            "fieldtype": "Data",
            "label": "REM Site",
            "insert_after": "custom_rem_type",
        },
        {
            "fieldname": "custom_rem_status",
            "fieldtype": "Select",
            "label": "REM Status",
            "options": "\nOperational\nUnder Repair\nIdle\nMaintenance",
            "default": "Operational",
            "insert_after": "custom_rem_site",
        },
        {
            "fieldname": "custom_rem_hours",
            "fieldtype": "Data",
            "label": "REM Hours",
            "insert_after": "custom_rem_status",
        },
        {
            "fieldname": "custom_rem_fuel_cost",
            "fieldtype": "Currency",
            "label": "REM Fuel Cost (BDT)",
            "insert_after": "custom_rem_hours",
        },
        {
            "fieldname": "custom_rem_operator",
            "fieldtype": "Data",
            "label": "REM Operator",
            "insert_after": "custom_rem_fuel_cost",
        },
        {
            "fieldname": "custom_rem_last_service",
            "fieldtype": "Date",
            "label": "REM Last Service",
            "insert_after": "custom_rem_operator",
        },
    ],
}

create_custom_fields(fields, ignore_validate=True)
frappe.db.commit()
for dt in ("Supplier", "Asset"):
    rows = frappe.get_all("Custom Field", filters={"dt": dt, "fieldname": ["like", "custom_rem%"]}, fields=["fieldname"])
    print(dt, "custom fields:", len(rows))
