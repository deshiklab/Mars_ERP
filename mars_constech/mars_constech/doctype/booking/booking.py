# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, date_diff


class Booking(Document):
	def validate(self):
		self.update_payment_summary()

	def update_payment_summary(self):
		"""Recompute Total Paid / Total Due / Days Overdue from installments.

		Ripple logic (mirrors REM V10):
		- total_paid  = sum of installment.paid_amount
		- total_due   = total_price - total_paid
		- days_overdue = days past the installment due date for the
		  oldest unpaid installment (0 if nothing overdue)
		"""
		total_paid = sum((row.paid_amount or 0) for row in self.installments)
		self.total_paid = total_paid
		self.total_due = max((self.total_price or 0) - total_paid, 0)

		# days overdue: find oldest installment that is unpaid and past due
		oldest_unpaid = None
		for row in self.installments:
			paid = row.paid_amount or 0
			due = row.amount or 0
			if due and paid < due and row.due_date and row.due_date < today():
				if not oldest_unpaid or row.due_date < oldest_unpaid.due_date:
					oldest_unpaid = row

		if oldest_unpaid:
			self.days_overdue = date_diff(today(), oldest_unpaid.due_date)
			if not self.due_date:
				self.due_date = oldest_unpaid.due_date
		else:
			self.days_overdue = 0
