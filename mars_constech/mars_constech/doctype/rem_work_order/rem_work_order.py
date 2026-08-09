# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class REMWorkOrder(Document):
	def validate(self):
		if self.deadline and self.date and self.deadline < self.date:
			frappe.throw("Deadline cannot be before the work order date")

	def autoname(self):
		prefix = "WO-"
		last = frappe.db.sql(
			"SELECT name FROM `tabREM Work Order` WHERE name LIKE %s ORDER BY creation DESC LIMIT 1",
			prefix + "%",
		)
		if last:
			try:
				n = int(str(last[0][0]).split("-")[-1]) + 1
			except Exception:
				n = 1
		else:
			n = 1
		self.name = f"{prefix}{n:03d}"
		self.wo_ref = self.name
