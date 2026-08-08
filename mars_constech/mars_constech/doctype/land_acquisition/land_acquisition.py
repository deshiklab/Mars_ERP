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

# Standard legal/land checklist the legal team must collect and vet during
# Due Diligence (Bangladesh land practice). Auto-loaded when a record enters
# the Due Diligence stage. Each item: (check_item, required, required_document)
STANDARD_LEGAL_CHECKLIST = [
	("CS Khatian", 1, "Certified copy of CS khatian showing the record of right"),
	("SA Khatian", 1, "Certified copy of SA khatian (1950s settlement record)"),
	("RS Khatian", 1, "Certified copy of RS khatian (latest survey record)"),
	("Original Sale Deed", 1, "Original deed / dakil of the current owner (registered)"),
	("Mutation Certificate", 1, "Mutation in the name of the seller (land office)"),
	("Land Development Tax Receipt", 1, "Up-to-date land development tax payment receipt"),
	("Holding / Property Tax Receipt", 1, "Current holding tax receipt (city corporation/union)"),
	("Non-Encumbrance Certificate", 1, "Certificate of non-encumbrance from the sub-registry"),
	("Court Case Search", 1, "Certificate from the civil court that no suit/litigation is pending"),
	("Survey Map (Mouza Map)", 1, "Latest mouza/survey map showing the dag and plot"),
	("Seller NID & Photo", 1, "Copy of the seller's NID and recent photograph"),
	("Board Resolution / POA", 0, "Board resolution or power of attorney (if seller is an entity)"),
	("NOC from Relevant Authority", 0, "NOC (RAJUK / city corporation / utility) if required"),
	("Possession Proof", 1, "Evidence of khas possession (possession letter / local verification)"),
]


class LandAcquisition(Document):
	def validate(self):
		self.validate_stage_transition()
		self.update_feasibility_score()
		self.update_risk_rating()
		self.compute_commission()
		self.compute_financials()
		self.load_standard_checklist_on_due_diligence()
		self.update_legal_checklist_progress()
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
			# The legal team must have collected AND vetted every required
			# document on the checklist before money is discussed.
			if not self.legal_checklist:
				frappe.throw(
					_("The legal checklist is empty. Load the standard checklist and "
					  "have the legal team vet the documents before Negotiation."),
					title=_("Negotiation Prerequisites"),
				)
			unverified = [
				row.check_item
				for row in self.legal_checklist
				if row.is_required and row.status not in ("Verified", "Not Applicable")
			]
			if unverified:
				frappe.throw(
					_("These required documents are not yet vetted by the legal team: {0}. "
					  "Each must be 'Verified' (or 'Not Applicable') before Negotiation.").format(
						", ".join(unverified[:5])
					),
					title=_("Negotiation Prerequisites"),
				)
			if self.legal_status != "Cleared":
				frappe.throw(
					_("Legal Status must be 'Cleared' before Negotiation. "
					  "The legal team must complete and approve the vetting."),
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
	# Legal checklist: standard template + progress
	# ------------------------------------------------------------------
	def load_standard_checklist_on_due_diligence(self):
		"""Auto-load the standard legal checklist when the record enters (or is
		already in) the Due Diligence stage and the checklist is empty."""
		if self.current_stage != "Due Diligence":
			return
		if self.legal_checklist:
			return
		self.load_standard_checklist()

	def load_standard_checklist(self):
		"""Append the standard legal/land checklist rows."""
		for item, required, doc_desc in STANDARD_LEGAL_CHECKLIST:
			self.append(
				"legal_checklist",
				{
					"check_item": item,
					"is_required": required,
					"required_document": doc_desc,
					"status": "Pending",
				},
			)

	@frappe.whitelist()
	def load_checklist_from_form(self):
		"""Form action: load the standard legal checklist (idempotent)."""
		if not self.legal_checklist:
			self.load_standard_checklist()
			self.save(ignore_permissions=True)
			return {"ok": True, "count": len(self.legal_checklist)}
		return {"ok": True, "count": len(self.legal_checklist), "already_loaded": True}

	def update_legal_checklist_progress(self):
		"""Percent of required items vetted (Verified or Not Applicable)."""
		required = [row for row in self.legal_checklist if row.is_required]
		if not required:
			self.legal_checklist_progress = 0
			return
		vetted = [
			row for row in required if row.status in ("Verified", "Not Applicable")
		]
		self.legal_checklist_progress = round(len(vetted) / len(required) * 100, 0)

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
	# Financial model (mirrors the V10 landFinancials() exactly):
	#   total cost = deal + registration fee + commission + legal +
	#                soil test + earth filling + boundary wall + misc
	#   ROI = (expected revenue - total cost) / total cost
	# ------------------------------------------------------------------
	def compute_financials(self):
		deal = self.deal_value or self.negotiated_price or self.asking_price or 0
		if not deal:
			self.total_project_cost = 0
			self.net_profit_est = 0
			self.estimated_roi = 0
			return

		reg_fee = deal * (self.registration_pct or 12) / 100.0
		misc = deal * (self.misc_pct or 5) / 100.0
		dev_costs = (
			(self.legal_cost or 0)
			+ (self.soil_test_cost or 0)
			+ (self.earth_filling_cost or 0)
			+ (self.boundary_wall_cost or 0)
		)
		self.total_project_cost = round(
			deal + reg_fee + (self.commission_amount or 0) + dev_costs + misc, 0
		)

		if self.expected_revenue:
			self.net_profit_est = round(self.expected_revenue - self.total_project_cost, 0)
			if self.total_project_cost:
				self.estimated_roi = round(
					(self.net_profit_est / self.total_project_cost) * 100.0, 1
				)
			else:
				self.estimated_roi = 0
		else:
			self.net_profit_est = 0
			self.estimated_roi = 0

	# ------------------------------------------------------------------
	# Handoff: turn an acquired land parcel into a real ERPNext Project
	# (B milestone — the prototype's "Merge to Project / Create Project")
	# ------------------------------------------------------------------
	@frappe.whitelist()
	def create_project_from_acquisition(self):
		"""At Possession, create (or link) a real ERPNext Project so the land
		becomes a development project with its own budget and lifecycle.

		- If target_project is already set: just returns it.
		- Otherwise creates a Project named after the parcel and links it.
		"""
		if self.current_stage not in ("Registration", "Possession"):
			frappe.throw(
				_("Project handoff is only available from the Registration or "
				  "Possession stage."),
				title=_("Project Handoff"),
			)
		if self.target_project:
			return {"project": self.target_project, "created": False}

		project_name = "{0} - {1}".format(
			self.land_acquisition_title or "Land Parcel",
			self.mouza or self.land_location or self.name,
		)
		project = frappe.get_doc(
			{
				"doctype": "Project",
				"project_name": project_name,
				"status": "Open",
				"expected_start_date": self.acquisition_date,
				"notes": "Created from Land Acquisition {0} (deal {1}).".format(
					self.name, self.deal_value or 0
				),
				"custom_acquisition_reference": self.name,
			}
		)
		project.flags.ignore_permissions = True
		project.insert(ignore_permissions=True)

		self.target_project = project.name
		self.save(ignore_permissions=True)
		return {"project": project.name, "created": True}

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
