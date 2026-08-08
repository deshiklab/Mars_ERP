# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectLifecycle(Document):
	def validate(self):
		self.log_stage_transition()
		if self.status == "Completed" and not self.actual_end_date:
			self.actual_end_date = frappe.utils.today()

	def log_stage_transition(self):
		"""Append an audit entry when current_stage changes (idempotent)."""
		if not self.get("__islocal") and self.current_stage:
			old_stage = frappe.db.get_value(
				"Project Lifecycle", self.name, "current_stage"
			)
			if old_stage and old_stage != self.current_stage:
				last = self.stage_transitions[-1].stage if self.stage_transitions else None
				if last != self.current_stage:
					self.append(
						"stage_transitions",
						{
							"stage": self.current_stage,
							"changed_on": frappe.utils.now(),
							"changed_by": frappe.session.user_fullname
							or frappe.session.user,
						},
					)
