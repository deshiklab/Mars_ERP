# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LandAcquisition(Document):
	def validate(self):
		self.update_feasibility_score()
		self.log_stage_transition()

	def update_feasibility_score(self):
		"""Weighted average of the scorecard: Σ(score/5 × weight) / Σ(weight) × 100."""
		total_weight = sum((row.weight or 0) for row in self.scorecard)
		if total_weight:
			weighted = sum(
				((row.score or 0) / 5.0) * (row.weight or 0) for row in self.scorecard
			)
			self.feasibility_score = round((weighted / total_weight) * 100, 1)
		elif self.scorecard:
			avg = sum((row.score or 0) for row in self.scorecard) / len(self.scorecard)
			self.feasibility_score = round((avg / 5.0) * 100, 1)
		else:
			self.feasibility_score = 0

	def log_stage_transition(self):
		"""Append an audit entry when current_stage changes (idempotent — compares
		against the persisted stage, so re-saving without a change adds nothing)."""
		if not self.get("__islocal") and self.current_stage:
			old_stage = frappe.db.get_value(
				"Land Acquisition", self.name, "current_stage"
			)
			if old_stage and old_stage != self.current_stage:
				# avoid duplicates if validate runs twice in one save cycle
				last = self.stage_log[-1].stage if self.stage_log else None
				if last != self.current_stage:
					self.append(
						"stage_log",
						{
							"stage": self.current_stage,
							"changed_on": frappe.utils.now(),
							"changed_by": frappe.session.user_fullname
							or frappe.session.user,
						},
					)
