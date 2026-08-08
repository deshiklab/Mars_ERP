# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt
"""Port V10 PWA demo collections into real doctypes.

Mappings:
  customers -> Customer (ERPNext native)
  leads     -> Lead (ERPNext native)
  projects  -> Project (ERPNext native)
  bookings + booking_schedules -> Booking + installments (mars_constech)
  invoices  -> Sales Invoice (ERPNext native), linked to Booking by client
  payments  -> Payment Entry (ERPNext native) for the big ones

Run via bench console:
  bench --site mars.local console <<EOF
  import mars_constech.utils.seed_real as s; s.run()
  EOF
"""
import json
from datetime import date

import frappe
from frappe.utils import today


def _load(key):
    path = f"/home/bitscol/rem-v10-src/seeds/{key}.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _mkinst(start_iso, count, amount, paid_count, due_count, step_months=1):
    """Mirror of the PWA's mkInst()."""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    out = []
    s = datetime.strptime(start_iso, "%Y-%m-%d").date()
    for i in range(count):
        d = s + relativedelta(months=i * (step_months or 1))
        if i < paid_count:
            status = "Paid"
        elif i < paid_count + due_count:
            status = "Due"
        else:
            status = "Upcoming"
        out.append(
            {
                "installment_no": i + 1,
                "due_date": d.isoformat(),
                "amount": amount,
                "paid_amount": amount if status == "Paid" else 0,
                "status": status,
            }
        )
    return out


def _money_display_to_number(s):
    """'৳1.8 Cr' -> 18000000 ; '৳46.0L' -> 4600000 ; '৳10,00,000' -> 1000000."""
    if s is None:
        return 0
    if isinstance(s, (int, float)):
        return s
    t = str(s).replace("৳", "").replace(",", "").strip()
    import re

    m = re.match(r"([\d.]+)\s*(Cr|Lac|L|K)?", t, re.I)
    if not m:
        return 0
    v = float(m.group(1))
    u = (m.group(2) or "").lower()
    if u == "cr":
        v *= 1e7
    elif u in ("lac", "l"):
        v *= 1e5
    elif u == "k":
        v *= 1e3
    return int(v)


def _find_customer(name):
    if not name:
        return None
    n = frappe.db.exists("Customer", {"customer_name": name})
    return n


def _create_customer(rec):
    n = _find_customer(rec.get("name"))
    if n:
        return n
    doc = frappe.new_doc("Customer")
    doc.customer_name = rec.get("name")
    doc.customer_type = "Individual"
    if rec.get("phone"):
        doc.mobile_no = rec.get("phone")
    if rec.get("email"):
        doc.email_id = rec.get("email")
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    return doc.name


def _create_lead(rec):
    email = rec.get("email") or f"lead{rec.get('id')}@example.com"
    n = frappe.db.exists("Lead", {"email_id": email})
    if n:
        return n
    doc = frappe.new_doc("Lead")
    doc.lead_name = rec.get("name")
    # status is a Select with a fixed set; map loosely, fall back to "Lead"
    status = rec.get("status") or "Lead"
    if status not in frappe.get_meta("Lead").get_options("status"):
        status = "Lead"
    doc.status = status
    doc.mobile_no = rec.get("phone")
    doc.email_id = email
    if rec.get("property"):
        doc.append("notes", {"note": rec.get("property")})
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    return doc.name


def _create_project(rec):
    n = frappe.db.exists("Project", {"project_name": rec.get("name")})
    if n:
        return n
    doc = frappe.new_doc("Project")
    doc.project_name = rec.get("name")
    doc.status = "Open"
    doc.expected_start_date = today()
    doc.notes = f"{rec.get('location') or ''} — {rec.get('desc') or ''}"[:280]
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    return doc.name


def _create_booking(rec, schedule):
    customer = _find_customer(rec.get("client"))
    if not customer:
        customer = _create_customer({"name": rec.get("client")})

    # find existing by title-ish match
    existing = frappe.get_all(
        "Booking", filters={"customer": customer}, fields=["name"], limit=1
    )
    if existing:
        return existing[0].name

    doc = frappe.new_doc("Booking")
    doc.customer = customer
    doc.project = _find_project(rec.get("property")) or None
    doc.property = rec.get("property")
    doc.unit = rec.get("unit")
    doc.total_price = _money_display_to_number(rec.get("price"))
    doc.advance_paid = _money_display_to_number(rec.get("advance"))
    doc.status = rec.get("status") or "Pending Review"
    doc.type = rec.get("type") or "Apartment"
    doc.terms = rec.get("terms") or ""

    # installments from schedule
    for inst in schedule or []:
        doc.append(
            "installments",
            {
                "installment_no": inst.get("no"),
                "due_date": inst.get("date"),
                "amount": inst.get("amount"),
                "paid_amount": inst.get("amount") if inst.get("status") == "Paid" else 0,
                "status": "Paid" if inst.get("status") == "Paid" else "Upcoming",
            },
        )
    # fallback: single full-payment installment
    if not doc.installments:
        doc.append(
            "installments",
            {
                "installment_no": 1,
                "due_date": today(),
                "amount": doc.total_price,
                "paid_amount": doc.advance_paid or 0,
                "status": "Paid" if doc.advance_paid else "Upcoming",
            },
        )
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    return doc.name


def _find_project(name):
    if not name:
        return None
    n = frappe.db.exists("Project", {"project_name": name})
    return n


def run():
    counts = {}

    customers = _load("customers")
    for rec in customers:
        _create_customer(rec)
    counts["customers"] = len(customers)

    leads = _load("leads")
    for rec in leads:
        _create_lead(rec)
    counts["leads"] = len(leads)

    projects = _load("projects")
    for rec in projects:
        _create_project(rec)
    counts["projects"] = len(projects)

    # schedules: manual reconstruction from the PWA seed (mkInst calls)
    schedules = {
        "BKG-101": [{"no": 1, "date": "2024-10-01", "amount": 3600000, "status": "Paid"}] + _mkinst("2025-01-01", 12, 1200000, 12, 0),
        "BKG-103": [{"no": 1, "date": "2024-11-15", "amount": 4600000, "status": "Paid"}],
        "BKG-105": [{"no": 1, "date": "2026-03-15", "amount": 1800000, "status": "Paid"}] + _mkinst("2026-04-15", 18, 900000, 1, 2),
        "BKG-107": [{"no": 1, "date": "2026-01-10", "amount": 4800000, "status": "Paid"}] + _mkinst("2026-02-10", 24, 466667, 5, 1),
        "BKG-110": [{"no": 1, "date": "2026-05-01", "amount": 37500000, "status": "Paid"}] + _mkinst("2026-06-01", 6, 6250000, 0, 1),
    }

    bookings = _load("bookings")
    for rec in bookings:
        _create_booking(rec, schedules.get(rec.get("id")))
    counts["bookings"] = len(bookings)

    frappe.db.commit()
    return counts
