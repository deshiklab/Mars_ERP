# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

# The practical acquisition pipeline (mirrors the V10 prototype):
#   Lead -> Due Diligence -> Negotiation -> Agreement -> Registration -> Possession
STAGES = [
	"Lead",
	"Due Diligence",
	"Negotiation",
	"Agreement",
	"Registration",
	"Possession",
]


class LandAcquisition(Document):
	def validate(self):
		self.validate_stage_transition()
		self.update_feasibility_score()
		self.update_risk_rating()
		self.compute_commission()
		self.log_stage_transition()

	# ------------------------------------------------------------------
	# Stage gates — the "practically correct" part: you cannot jump stages
	# or advance before the previous stage's work is actually done.
	# ------------------------------------------------------------------
	def validate_stage_transition(self):
		"""Enforce the pipeline order and per-stage prerequisites."""
		if self.get("__islocal") or not self.current_stage:
			return

		old_stage = frappe.db.get_value("Land Acquisition", self.name, "current_stage")
		if not old_stage or old_stage == self.current_stage:
			return

		old_idx = STAGES.index(old_stage) if old_stage in STAGES else -1
		new_idx = STAGES.index(self.current_stage) if self.current_stage in STAGES else -1

		# No skipping ahead by more than one stage at a time
		if new_idx > old_idx + 1:
			frappe.throw(
				_("Cannot move from {0} straight to {1}. Advance one stage at a time: {2}").format(
					old_stage, self.current_stage, " → ".join(STAGES)
				),
				title=_("Invalid Stage Transition"),
			)

		# Per-stage prerequisites (only enforced when moving FORWARD)
		if new_idx > old_idx:
			self.check_stage_prerequisites(new_idx)

	def check_stage_prerequisites(self, new_idx):
		"""What must be true before the record may enter each stage."""
		stage = STAGES[new_idx]

		if stage == "Due Diligence":
			# must have basic identity of the land before investigating it
			missing = [
				label
				for field, label in (
					("land_location", _("Location")),
					("land_owner", _("Land Owner")),
					("area_katha", _("Area (Katha)")),
					("asking_price", _("Asking Price")),
				)
				if not self.get(field)
			]
			if missing:
				frappe.throw(
					_("Complete the following before starting Due Diligence: {0}").format(
						", ".join(missing)
					),
					title=_("Due Diligence Prerequisites"),
				)

		elif stage == "Negotiation":
			# title must be investigated before money talks
			if self.litigation_check != "Clear":
				frappe.throw(
					_("Litigation check must be 'Clear' before Negotiation. "
					  "Resolve title issues first."),
					title=_("Negotiation Prerequisites"),
				)
			if not self.khatian_cs and not self.khatian_sa and not self.khatian_rs:
				frappe.throw(
					_("Record at least one khatian number (CS/SA/RS) before Negotiation."),
					title=_("Negotiation Prerequisites"),
				)

		elif stage == "Agreement":
			# need a price agreed before signing anything
			if not self.negotiated_price:
				frappe.throw(
					_("Set the Negotiated Price before moving to Agreement."),
					title=_("Agreement Prerequisites"),
				)
			if not self.deal_value:
				frappe.throw(
					_("Set the Deal Value before moving to Agreement."),
					title=_("Agreement Prerequisites"),
				)

		elif stage == "Registration":
			# legal must be fully cleared before registering a deed
			if self.legal_status != "Cleared":
				frappe.throw(
					_("Legal Status must be 'Cleared' before Registration. "
					  "Complete the legal checklist first."),
					title=_("Registration Prerequisites"),
				)
			if not self.documents:
				frappe.throw(
					_("Add the required documents to the Document Registry before Registration."),
					title=_("Registration Prerequisites"),
				)

		elif stage == "Possession":
			# must have an acquisition/registration date to hand over
			if not self.acquisition_date:
				frappe.throw(
					_("Set the Acquisition / Registration Date before Possession."),
					title=_("Possession Prerequisites"),
				)

	# ------------------------------------------------------------------
	# Feasibility score: weighted scorecard with practical criteria
	# ------------------------------------------------------------------
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

	# ------------------------------------------------------------------
	# Risk rating: derived from the practical risk inputs
	# ------------------------------------------------------------------
	def update_risk_rating(self):
		"""Overall risk from litigation, flood, and legal status — recomputed
		deterministically on every save so it downgrades when issues resolve.

		- litigation Issues Found / flood High        -> High
		- litigation Pending / flood Medium / legal Issues -> Medium
		- otherwise                                   -> Low
		"""
		if (
			self.litigation_check == "Issues Found"
			or self.flood_risk == "High"
		):
			self.risk_rating = "High"
		elif (
			self.litigation_check == "Pending"
			or self.flood_risk == "Medium"
			or self.legal_status == "Issues Found"
		):
			self.risk_rating = "Medium"
		else:
			self.risk_rating = "Low"

	# ------------------------------------------------------------------
	# Commission auto-calc: % of the deal value
	# ------------------------------------------------------------------
	def compute_commission(self):
		if self.deal_value and self.commission_pct:
			self.commission_amount = round(self.deal_value * self.commission_pct / 100.0, 0)

	# ------------------------------------------------------------------
	# Stage audit trail
	# ------------------------------------------------------------------
	def log_stage_transition(self):
		"""Append an audit entry when current_stage changes."""
		if not self.get("__islocal") and self.current_stage:
			old_stage = frappe.db.get_value(
				"Land Acquisition", self.name, "current_stage"
			)
			if old_stage and old_stage != self.current_stage:
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
