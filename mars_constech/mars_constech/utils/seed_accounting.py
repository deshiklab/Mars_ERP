# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt
"""Port V10 invoices + payments into ERPNext accounting.

  invoices (INV-*)  -> Sales Invoice (native) with items
  invoices (PINV-*) -> Purchase Invoice (native) + Supplier records
  payments          -> Payment Entry (native), referenced to sales invoices

Run via bench console:
  import mars_constech.mars_constech.utils.seed_accounting as sa; sa.run()
"""
import json

import frappe
from frappe.utils import today

COMPANY = "Mars Constact"


def _load(key):
    path = f"/home/bitscol/rem-v10-src/seeds/{key}.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _find_customer(name):
    if not name:
        return None
    return frappe.db.exists("Customer", {"customer_name": name})


def _ensure_customer(name):
    n = _find_customer(name)
    if n:
        return n
    doc = frappe.new_doc("Customer")
    doc.customer_name = name
    doc.customer_type = "Individual"
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    return doc.name


def _ensure_supplier(name):
    n = frappe.db.exists("Supplier", {"supplier_name": name})
    if n:
        return n
    doc = frappe.new_doc("Supplier")
    doc.supplier_name = name
    doc.supplier_group = "All Supplier Groups"
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    return doc.name


def _ensure_item(desc, rate):
    """Create a reusable item named by description if missing."""
    n = frappe.db.exists("Item", {"item_name": desc})
    if n:
        return n
    doc = frappe.new_doc("Item")
    doc.item_code = desc[:140]
    doc.item_name = desc
    doc.item_group = "All Item Groups"
    doc.stock_uom = "Nos"
    doc.is_stock_item = 0
    doc.standard_rate = rate
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    return doc.name


def _account(account_type):
    c = frappe.get_doc("Company", COMPANY)
    return c.get(account_type)


def _create_sales_invoice(rec):
    customer = _ensure_customer(rec.get("client"))
    # find by customer + grand_total
    existing = frappe.get_all(
        "Sales Invoice",
        filters={"customer": customer, "grand_total": rec.get("amount")},
        fields=["name"],
        limit=1,
    )
    if existing:
        return existing[0].name

    doc = frappe.new_doc("Sales Invoice")
    doc.customer = customer
    doc.company = COMPANY
    doc.set_posting_time = 1  # keep the historical posting date
    doc.posting_date = rec.get("issuedDate") or today()
    due = rec.get("dueDate")
    if due and due < (rec.get("issuedDate") or today()):
        due = rec.get("issuedDate")
    doc.due_date = due
    doc.remarks = rec.get("desc") or ""
    for it in rec.get("items", []):
        item = _ensure_item(it.get("desc"), it.get("rate"))
        doc.append(
            "items",
            {
                "item_code": item,
                "qty": it.get("qty", 1),
                "rate": it.get("rate"),
            },
        )
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)

    # Paid invoices get submitted (docstatus=1) so they book GL entries
    if rec.get("status") == "Paid":
        try:
            doc.submit()
        except Exception as e:
            frappe.log_error(f"SI submit failed {doc.name}: {e}", "seed_accounting")

    return doc.name


def _create_purchase_invoice(rec):
    supplier = _ensure_supplier(rec.get("client"))
    existing = frappe.get_all(
        "Purchase Invoice",
        filters={"supplier": supplier, "grand_total": rec.get("amount")},
        fields=["name"],
        limit=1,
    )
    if existing:
        return existing[0].name

    doc = frappe.new_doc("Purchase Invoice")
    doc.supplier = supplier
    doc.company = COMPANY
    doc.set_posting_time = 1  # keep the historical posting date
    doc.posting_date = rec.get("issuedDate") or today()
    due = rec.get("dueDate")
    if due and due < (rec.get("issuedDate") or today()):
        due = rec.get("issuedDate")
    doc.due_date = due
    doc.remarks = rec.get("desc") or ""
    for it in rec.get("items", []):
        item = _ensure_item(it.get("desc"), it.get("rate"))
        doc.append(
            "items",
            {
                "item_code": item,
                "qty": it.get("qty", 1),
                "rate": it.get("rate"),
            },
        )
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)
    if rec.get("status") == "Paid":
        try:
            doc.submit()
        except Exception as e:
            frappe.log_error(f"PI submit failed {doc.name}: {e}", "seed_accounting")
    return doc.name


def _create_payment(rec, si_outstanding):
    """Payment Entry against the matching sales invoice (by client), allocating
    at most the invoice's remaining outstanding amount."""
    party = _ensure_customer(rec.get("client"))
    existing = frappe.get_all(
        "Payment Entry",
        filters={"party": party, "paid_amount": rec.get("amount")},
        fields=["name"],
        limit=1,
    )
    if existing:
        return existing[0].name

    doc = frappe.new_doc("Payment Entry")
    doc.payment_type = "Receive"
    doc.party_type = "Customer"
    doc.party = party
    doc.company = COMPANY
    doc.set_posting_time = 1  # keep the historical posting date
    doc.posting_date = rec.get("date") or today()
    doc.paid_from = _account("default_receivable_account")
    doc.paid_to = _account("default_cash_account")
    doc.paid_amount = rec.get("amount")
    doc.received_amount = rec.get("amount")
    doc.reference_no = rec.get("reference") or ""
    doc.remarks = rec.get("notes") or f"Payment {rec.get('id')}"

    # link to the matching invoice, allocating only the remaining outstanding
    si = si_outstanding.get(rec.get("client"))
    if si:
        doc.append(
            "references",
            {
                "reference_doctype": "Sales Invoice",
                "reference_name": si[0],
                "allocated_amount": min(rec.get("amount"), si[1]),
            },
        )
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)
    try:
        doc.submit()
        # reduce outstanding after successful submit
        if si:
            si_outstanding[rec.get("client")][1] -= min(rec.get("amount"), si[1])
    except Exception as e:
        frappe.log_error(f"PE submit failed {doc.name}: {e}", "seed_accounting")
    return doc.name


def run():
    counts = {}

    # map client -> [paid sales invoice name, remaining outstanding] for
    # payment references (multiple payments can hit one invoice)
    si_outstanding = {}
    invs = _load("invoices")
    for rec in invs:
        if rec["id"].startswith("INV-"):
            name = _create_sales_invoice(rec)
            if rec.get("status") == "Paid":
                si_outstanding[rec.get("client")] = [name, rec.get("amount", 0)]
    counts["sales_invoices"] = len(frappe.get_all("Sales Invoice"))

    for rec in invs:
        if rec["id"].startswith("PINV-"):
            _create_purchase_invoice(rec)
    counts["purchase_invoices"] = len(frappe.get_all("Purchase Invoice"))

    pays = _load("payments")
    for rec in pays:
        _create_payment(rec, si_outstanding)
    counts["payment_entries"] = len(frappe.get_all("Payment Entry"))
    counts["suppliers"] = len(frappe.get_all("Supplier"))

    frappe.db.commit()
    return counts
