# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe

no_cache = 1


def get_context(context):
	"""Demo payment page — simulates the gateway's hosted checkout."""
	ref = frappe.form_dict.get("ref")
	gateway = frappe.form_dict.get("gateway", "bkash")
	invoice = frappe.form_dict.get("invoice", "")
	amount = frappe.form_dict.get("amount", "0")

	rec = frappe.cache().get_value(f"mars_demo_pay_{ref}") if ref else None
	context.ref = ref
	context.gateway = gateway
	context.invoice = invoice
	context.amount = amount
	context.valid = bool(rec) if ref else False
	if rec:
		context.invoice = rec.get("invoice", invoice)
		context.amount = rec.get("amount", amount)
		context.gateway = "bkash" if rec.get("gateway") == "bKash" else "nagad"
	context.confirm_url = f"/api/method/mars_constech.mars_constech.api.demo_confirm?ref={ref}"
	return context
