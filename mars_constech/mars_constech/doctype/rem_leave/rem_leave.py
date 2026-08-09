# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff


class REMLeave(Document):
    def validate(self):
        if self.from_date and self.to_date:
            if self.to_date < self.from_date:
                frappe.throw(_("To date cannot be before From date"))
            self.total_days = date_diff(self.to_date, self.from_date) + 1
