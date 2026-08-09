# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_exec_summary():
    """Cross-module KPIs for the REM Executive Dashboard page."""
    out = {}
    # Sales / CRM
    out["leads"] = frappe.db.count("Lead")
    out["bookings"] = frappe.db.count("REM Booking")
    out["booking_value"] = frappe.db.sql(
        "SELECT COALESCE(SUM(deal_value),0) FROM `tabREM Booking`")[0][0]
    out["customers"] = frappe.db.count("Customer")
    # Land
    out["land_acquisitions"] = frappe.db.count("Land Acquisition")
    out["land_pending_legal"] = frappe.db.sql(
        "SELECT COUNT(*) FROM `tabLand Acquisition` WHERE legal_status != 'Cleared' OR legal_status IS NULL"
    )[0][0]
    # Dues / Finance
    out["dues_outstanding"] = frappe.db.sql(
        "SELECT COALESCE(SUM(total_due),0) FROM `tabREM Booking` WHERE total_due > 0")[0][0]
    out["invoices_outstanding"] = frappe.db.sql(
        "SELECT COALESCE(SUM(outstanding_amount),0) FROM `tabSales Invoice` WHERE docstatus=1 AND outstanding_amount > 0"
    )[0][0]
    out["invoices_paid"] = frappe.db.count("Sales Invoice", filters={"docstatus": 1, "outstanding_amount": 0})
    # HR
    out["employees"] = frappe.db.count("Employee", filters={"status": "Active"})
    out["attendance_today"] = frappe.db.count("REM Attendance", filters={"attendance_date": frappe.utils.today()})
    out["leave_pending"] = frappe.db.count("REM Leave", filters={"status": "Pending"})
    out["labor"] = frappe.db.count("REM Labor", filters={"status": "Present"})
    # Stock
    out["stock_items"] = frappe.db.count("Item", filters={"custom_rem_ref": ["is", "set"]})
    out["low_stock"] = frappe.db.sql(
        "SELECT COUNT(*) FROM `tabItem` WHERE custom_rem_ref IS NOT NULL AND disabled=0 "
        "AND (SELECT COALESCE(SUM(actual_qty),0) FROM `tabBin` WHERE item_code=`tabItem`.name) < custom_reorder_level"
    )[0][0]
    out["pos_open"] = frappe.db.count("Purchase Order", filters={"docstatus": 0})
    # Construction
    out["projects"] = frappe.db.count("Project")
    out["work_orders"] = frappe.db.count("REM Work Order")
    out["handovers_pending"] = frappe.db.count("REM Handover",
        filters={"status": ["in", ["Construction Ongoing", "Inspection Pending", "Handover Scheduled"]]})
    out["approvals_pending"] = frappe.db.count("REM Approval", filters={"status": "Pending"})
    # Assets / Other
    out["assets"] = frappe.db.count("Asset", filters={"status": "Submitted"})
    out["tickets_open"] = frappe.db.count("Issue", filters={"status": ["in", ["Open", "Replied"]]})
    return out
