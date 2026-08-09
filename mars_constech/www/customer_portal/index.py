# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	"""Customer portal: bookings, installments, invoices, payments for the
	logged-in portal user's linked Customer record."""
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	customer = _get_portal_customer()
	if not customer:
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	context.customer = customer
	context.no_cache = 1

	# bookings for this customer
	context.bookings = frappe.get_all(
		"REM Booking",
		filters={"customer_name": customer},
		fields=[
			"name", "project_name", "unit", "deal_value", "advance_paid",
			"total_paid", "total_due", "status", "creation", "booking_type",
		],
		order_by="creation desc",
		limit_page_length=50,
	)

	# installments across all their bookings
	context.installments = []
	booking_names = [b.name for b in context.bookings]
	if booking_names:
		context.installments = frappe.get_all(
			"REM Booking Installment",
			filters=[["parent", "in", booking_names]],
			fields=["parent", "installment_no", "due_date", "amount", "status"],
			order_by="due_date asc",
			limit_page_length=200,
		)

	# sales invoices for this customer
	context.invoices = frappe.get_all(
		"Sales Invoice",
		filters={"customer": customer},
		fields=[
			"name", "grand_total", "outstanding_amount", "status",
			"posting_date", "due_date",
		],
		order_by="posting_date desc",
		limit_page_length=50,
	)
	invoice_names = [i.name for i in context.invoices]

	# payments for this customer (with method/reference)
	context.payments = frappe.get_all(
		"Payment Entry",
		filters={"party": customer},
		fields=[
			"name", "posting_date", "paid_amount", "reference_no",
			"remarks", "mode_of_payment",
		],
		order_by="posting_date desc",
		limit_page_length=50,
	)

	# payment allocation per invoice (method + ref joined for display)
	context.invoice_payments = {}
	if invoice_names:
		alloc = frappe.db.sql(
			"""
			SELECT pr.reference_name, pe.posting_date, pe.paid_amount,
			       pe.mode_of_payment, pe.reference_no
			FROM `tabPayment Entry Reference` pr
			JOIN `tabPayment Entry` pe ON pe.name = pr.parent
			WHERE pr.reference_doctype = 'Sales Invoice'
			  AND pr.reference_name IN %s
			ORDER BY pe.posting_date
			""",
			(tuple(invoice_names),),
			as_dict=True,
		)
		for a in alloc:
			context.invoice_payments.setdefault(a.reference_name, []).append(a)

	# totals
	context.totals = {
		"bookings": len(context.bookings),
		"booked_value": sum(b.deal_value or 0 for b in context.bookings),
		"paid": sum(b.total_paid or 0 for b in context.bookings),
		"due": sum(b.total_due or 0 for b in context.bookings),
		"invoices": len(context.invoices),
		"invoice_outstanding": sum(i.outstanding_amount or 0 for i in context.invoices),
		"payments": len(context.payments),
		"payments_total": sum(p.paid_amount or 0 for p in context.payments),
	}

	# payment-alert banner: any booking with due > 0
	context.alert = None
	overdue = [b for b in context.bookings if (b.total_due or 0) > 0]
	if overdue:
		biggest = max(overdue, key=lambda b: b.total_due or 0)
		context.alert = {
			"type": "due",
			"title": _("Payment due"),
			"message": _("{0} has ৳{1} outstanding. Please contact our accounts team to arrange payment.").format(
				biggest.project_name or biggest.name,
				_round_cr(biggest.total_due),
			),
		}

	# support contact (safe lookups with fallbacks)
	context.support = {
		"phone": _safe_single_value("Support Settings", "support_phone")
		or _safe_single_value("Support Settings", "phone")
		or "+880 1711-000000",
		"email": _safe_single_value("Support Settings", "support_email")
		or "accounts@marsconstech.com",
	}

	return context


def _safe_single_value(doctype, field):
	"""get_single_value that returns None instead of raising on missing fields."""
	try:
		return frappe.db.get_single_value(doctype, field)
	except Exception:
		return None


def _get_portal_customer():
	"""Resolve the portal user's Customer via User Permission (allow=Customer)."""
	user = frappe.session.user
	perms = frappe.get_all(
		"User Permission",
		filters={"user": user, "allow": "Customer"},
		fields=["for_value"],
		limit=1,
	)
	if perms:
		return perms[0].for_value
	return None


def _round_cr(v):
	"""Format taka to a compact ৳Cr/৳Lac string."""
	if not v:
		return "৳0"
	if v >= 10000000:
		return f"৳{v / 10000000:.1f} Cr"
	if v >= 100000:
		return f"৳{v / 100000:.1f} Lac"
	return f"৳{v:,.0f}"
