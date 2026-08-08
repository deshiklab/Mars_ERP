# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt
"""Payment gateway adapters: bKash (Tokenized Checkout), Nagad, and a
sandbox/demo mode that simulates a gateway so the whole flow is testable
without merchant credentials.

Real-gateway integration points follow the official API shapes:

  bKash Tokenized Checkout:
    POST https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/checkout/token/grant
        {app_key, app_secret}  ->  {id_token}
    POST .../tokenized/checkout/create
        {mode:"0011", payerReference, callbackURL, amount, currency:"BDT",
         intent:"sale", merchantInvoiceNumber}  ->  {bkashURL, paymentID}
    POST .../tokenized/checkout/execute  {paymentID}  ->  {transactionStatus, trxID}

  Nagad:
    POST https://api.mynagad.com/api/check-out/initialize/{merchantId}/{orderId}
        (signed)  ->  {callbackUrl}
    GET  callback  ->  verify via {merchantId}/{orderId} status endpoint
"""

import frappe
from frappe import _

SETTINGS = "Mars Payment Gateway Settings"
COMPANY = "Mars Constact"

# default URLs (sandbox)
BKASH_BASE = "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/checkout"
NAGAD_BASE = "https://api.mynagad.com"


def get_settings():
	return frappe.get_single(SETTINGS)


def _random_ref():
	import uuid

	return uuid.uuid4().hex[:12].upper()


# --------------------------------------------------------------------------
# Invoice → Payment Entry settlement (shared by all gateways)
# --------------------------------------------------------------------------
def settle_invoice(invoice_name, amount, method, reference):
	"""Create + submit a Payment Entry against the invoice. Idempotent per
	(method, reference)."""
	inv = frappe.get_doc("Sales Invoice", invoice_name)
	existing = frappe.db.exists(
		"Payment Entry",
		{"reference_no": reference, "party": inv.customer},
	)
	if existing:
		return existing

	from frappe.utils import nowdate

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Receive"
	pe.party_type = "Customer"
	pe.party = inv.customer
	pe.company = COMPANY
	pe.posting_date = nowdate()
	pe.paid_from = _account("default_receivable_account")
	pe.paid_to = _account("default_cash_account")
	pe.paid_amount = amount
	pe.received_amount = amount
	pe.reference_no = reference
	pe.remarks = f"Online payment via {method} ({reference})"
	pe.append(
		"references",
		{
			"reference_doctype": "Sales Invoice",
			"reference_name": invoice_name,
			"allocated_amount": min(amount, inv.outstanding_amount or amount),
		},
	)
	pe.flags.ignore_permissions = True
	pe.insert(ignore_permissions=True)
	pe.submit()
	frappe.db.commit()
	return pe.name


def _account(account_type):
	c = frappe.get_doc("Company", COMPANY)
	return c.get(account_type)


# --------------------------------------------------------------------------
# bKash adapter
# --------------------------------------------------------------------------
class BkashAdapter:
	name = "bKash"

	def __init__(self, settings):
		self.s = settings

	def create_payment(self, invoice, amount, callback_url):
		"""Create a bKash tokenized checkout session -> redirect URL."""
		if self.s.sandbox_mode:
			return self._demo_url(invoice, amount)
		import requests

		# 1. grant token
		r = requests.post(
			f"{BKASH_BASE}/token/grant",
			json={
				"app_key": self.s.bkash_app_key,
				"app_secret": self.s.get_password("bkash_app_secret"),
			},
			timeout=15,
		)
		token = r.json().get("id_token")
		headers = {
			"Authorization": token,
			"X-APP-Key": self.s.bkash_app_key,
			"Content-Type": "application/json",
		}
		# 2. create checkout
		r = requests.post(
			f"{BKASH_BASE}/create",
			json={
				"mode": "0011",
				"payerReference": invoice.customer,
				"callbackURL": callback_url,
				"amount": str(amount),
				"currency": "BDT",
				"intent": "sale",
				"merchantInvoiceNumber": invoice.name,
			},
			headers=headers,
			timeout=15,
		)
		data = r.json()
		return {"redirect": data.get("bkashURL"), "payment_id": data.get("paymentID")}

	def verify(self, payment_id):
		import requests

		r = requests.post(
			f"{BKASH_BASE}/execute",
			json={"paymentID": payment_id},
			headers={
				"Authorization": self._token(),
				"X-APP-Key": self.s.bkash_app_key,
				"Content-Type": "application/json",
			},
			timeout=15,
		)
		d = r.json()
		if d.get("transactionStatus") == "Completed":
			return {
				"success": True,
				"reference": d.get("trxID"),
				"amount": float(d.get("amount", 0)),
			}
		return {"success": False, "error": d.get("statusMessage")}

	def _token(self):
		import requests

		r = requests.post(
			f"{BKASH_BASE}/token/grant",
			json={"app_key": self.s.bkash_app_key, "app_secret": self.s.get_password("bkash_app_secret")},
			timeout=15,
		)
		return r.json().get("id_token")

	def _demo_url(self, invoice, amount):
		ref = _random_ref()
		frappe.cache().set_value(f"mars_demo_pay_{ref}", {"invoice": invoice.name, "amount": amount, "gateway": "bKash"}, expires_in_sec=3600)
		return {"redirect": f"/mars-pay-demo?ref={ref}&gateway=bkash&invoice={invoice.name}&amount={amount}", "payment_id": ref}


# --------------------------------------------------------------------------
# Nagad adapter
# --------------------------------------------------------------------------
class NagadAdapter:
	name = "Nagad"

	def __init__(self, settings):
		self.s = settings

	def create_payment(self, invoice, amount, callback_url):
		if self.s.sandbox_mode:
			ref = _random_ref()
			frappe.cache().set_value(f"mars_demo_pay_{ref}", {"invoice": invoice.name, "amount": amount, "gateway": "Nagad"}, expires_in_sec=3600)
			return {"redirect": f"/mars-pay-demo?ref={ref}&gateway=nagad&invoice={invoice.name}&amount={amount}", "payment_id": ref}
		# Real Nagad: initialize checkout (signed request). Requires merchant keys.
		order_id = _random_ref()
		import requests

		r = requests.post(
			f"{NAGAD_BASE}/api/check-out/initialize/{self.s.nagad_merchant_id}/{order_id}",
			json={
				"merchantCallbackURL": callback_url,
				"amount": str(amount),
				"currency": "BDT",
				"orderId": order_id,
			},
			timeout=15,
		)
		return {"redirect": r.json().get("callbackUrl"), "payment_id": order_id}

	def verify(self, payment_id):
		# Real verification requires the Nagad signed status endpoint; in
		# sandbox mode verification happens via the demo page.
		return {"success": False, "error": "Nagad live verification requires merchant keys"}


# --------------------------------------------------------------------------
# Facade
# --------------------------------------------------------------------------
def get_adapter(gateway):
	s = get_settings()
	if gateway == "bkash":
		return BkashAdapter(s)
	if gateway == "nagad":
		return NagadAdapter(s)
	frappe.throw(_("Unknown gateway: {0}").format(gateway))


def create_payment(invoice_name, gateway, amount=None):
	"""Entry point from the portal: returns {redirect, payment_id}."""
	inv = frappe.get_doc("Sales Invoice", invoice_name)
	outstanding = inv.outstanding_amount or inv.grand_total
	if amount is None or amount > outstanding:
		amount = outstanding
	if amount <= 0:
		frappe.throw(_("Invoice is already fully paid"))

	s = get_settings()
	if not s.enabled:
		frappe.throw(_("Online payments are disabled"))
	if not s.sandbox_mode and not s.get(gateway + "_enabled"):
		frappe.throw(_("{0} gateway is not enabled").format(gateway))

	callback = s.callback_url or (
		frappe.utils.get_url() + "/api/method/mars_constech.mars_constech.api.payment_callback"
	)
	adapter = get_adapter(gateway)
	return adapter.create_payment(inv, amount, callback)


def verify_and_settle(gateway, payment_id, invoice_name=None, amount=None):
	"""Verify a payment; on success settle the invoice. Returns (ok, message, pe_name)."""
	adapter = get_adapter(gateway)
	# demo mode: cached payment record acts as the "gateway confirmed" signal
	if get_settings().sandbox_mode:
		rec = frappe.cache().get_value(f"mars_demo_pay_{payment_id}")
		if not rec:
			return False, _("Payment session not found or expired"), None
		pe = settle_invoice(rec["invoice"], rec["amount"], adapter.name, f"DEMO-{payment_id}")
		frappe.cache().delete_value(f"mars_demo_pay_{payment_id}")
		return True, _("Payment received — thank you!"), pe

	res = adapter.verify(payment_id)
	if res.get("success"):
		pe = settle_invoice(
			invoice_name or payment_id,
			res.get("amount") or amount,
			adapter.name,
			res.get("reference") or payment_id,
		)
		return True, _("Payment received — thank you!"), pe
	return False, res.get("error") or _("Payment verification failed"), None
