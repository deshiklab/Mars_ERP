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
		"Booking",
		filters={"customer": customer},
		fields=[
			"name", "property", "unit", "total_price", "advance_paid",
			"total_paid", "total_due", "status", "booking_date", "type",
		],
		order_by="booking_date desc",
		limit_page_length=50,
	)

	# installments across all their bookings
	context.installments = []
	booking_names = [b.name for b in context.bookings]
	if booking_names:
		context.installments = frappe.get_all(
			"Booking Installment",
			filters=[["parent", "in", booking_names]],
			fields=["parent", "installment_no", "due_date", "amount", "paid_amount", "status"],
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

	# totals
	context.totals = {
		"bookings": len(context.bookings),
		"booked_value": sum(b.total_price or 0 for b in context.bookings),
		"paid": sum(b.total_paid or 0 for b in context.bookings),
		"due": sum(b.total_due or 0 for b in context.bookings),
		"invoices": len(context.invoices),
		"invoice_outstanding": sum(i.outstanding_amount or 0 for i in context.invoices),
	}

	return context


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
