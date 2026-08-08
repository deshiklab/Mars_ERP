# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class REMBooking(Document):
	def validate(self):
		self._compute_totals()

	def _compute_totals(self):
		"""Total paid/due from the installment child rows."""
		paid = sum((i.amount or 0) for i in self.installments if i.status == "Paid")
		due = sum((i.amount or 0) for i in self.installments if i.status == "Due")
		self.total_paid = paid
		self.total_due = due

	def autoname(self):
		"""BKG-YYYY-NNNN style name."""
		year = frappe.utils.now_datetime().year
		prefix = f"BKG-{year}-"
		last = frappe.db.sql(
			"SELECT name FROM `tabREM Booking` WHERE name LIKE %s ORDER BY creation DESC LIMIT 1",
			prefix + "%",
		)
		if last:
			try:
				n = int(str(last[0][0]).split("-")[-1]) + 1
			except Exception:
				n = 1
		else:
			n = 1
		self.name = f"{prefix}{n:04d}"
		self.booking_id = self.name
