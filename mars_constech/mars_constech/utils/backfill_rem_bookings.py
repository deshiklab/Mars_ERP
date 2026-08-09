import frappe, json
from datetime import date, timedelta

def _month_add(d, months):
    y, m = d.year + (d.month - 1 + months) // 12, (d.month - 1 + months) % 12 + 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date(y, m, day)

def backfill_rem_bookings():
    """REDO: wipe backfilled REM Bookings, re-migrate from legacy with correct
    installment statuses (Paid only when paid_amount >= amount) and
    reconstructed due dates (anchor = booking_date, monthly cadence)."""
    # wipe previous backfill (custom_booking_ref rows are all ours)
    names = frappe.db.sql_list("SELECT name FROM `tabREM Booking` WHERE custom_booking_ref IS NOT NULL")
    for n in names:
        frappe.delete_doc("REM Booking", n, force=1, ignore_permissions=True)
    frappe.db.commit()
    created = 0
    legacy = frappe.get_all("Booking", fields=["name", "customer", "property", "unit", "type",
                                               "status", "total_price", "advance_paid", "booking_date",
                                               "total_paid", "total_due", "due_date", "days_overdue"])
    for lb in legacy:
        inst_rows = frappe.get_all("Booking Installment",
                                   filters={"parent": lb.name},
                                   fields=["installment_no", "due_date", "amount", "paid_amount", "status"],
                                   order_by="installment_no")
        anchor = None
        if lb.booking_date:
            try: anchor = date.fromisoformat(str(lb.booking_date)[:10])
            except Exception: anchor = None
        if not anchor:
            anchor = date.today()
        first_date = None
        for r in inst_rows:
            if r.due_date:
                try: first_date = date.fromisoformat(str(r.due_date)[:10]); break
                except Exception: pass
        base = first_date or anchor
        doc = frappe.new_doc("REM Booking")
        doc.custom_booking_ref = lb.name
        doc.customer_name = lb.customer or ""
        doc.customer = lb.customer or ""
        doc.project_name = lb.property or ""
        doc.unit = lb.unit or ""
        doc.booking_type = lb.type or "Flat"
        doc.deal_value = lb.total_price or 0
        doc.advance_paid = lb.advance_paid or 0
        doc.status = lb.status or "Pending Review"
        doc.schedule_start = str(base)
        idx = 0
        for r in inst_rows:
            due = None
            if r.due_date:
                try: due = date.fromisoformat(str(r.due_date)[:10])
                except Exception: due = None
            if not due:
                due = _month_add(base, idx)
            # CORRECT status: Paid only when fully paid
            amount = r.amount or 0
            paid_amt = r.paid_amount or 0
            if amount and paid_amt >= amount:
                status = "Paid"
            else:
                status = "Due" if due < date.today() else "Upcoming"
            doc.append("installments", {
                "installment_no": r.installment_no or (idx + 1),
                "due_date": str(due),
                "amount": amount,
                "status": status,
            })
            idx += 1
        doc.save(ignore_permissions=True)
        created += 1
    frappe.db.commit()
    print(json.dumps({"created": created}))
