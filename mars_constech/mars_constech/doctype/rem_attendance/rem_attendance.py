# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff


class REMAttendance(Document):
    def validate(self):
        if self.status in ("Absent", "Leave", "Weekend", "Holiday"):
            self.in_time = None
            self.out_time = None
