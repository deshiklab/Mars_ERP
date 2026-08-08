# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe

STAGES = [
	"Lead",
	"Due Diligence",
	"Negotiation",
	"Agreement",
	"Registration",
	"Possession",
]

STAGE_COLORS = {
	"Lead": "blue",
	"Due Diligence": "cyan",
	"Negotiation": "orange",
	"Agreement": "purple",
	"Registration": "yellow",
	"Possession": "green",
}


@frappe.whitelist()
def get_pipeline():
	"""Return all Land Acquisition records grouped for the kanban."""
	records = frappe.get_all(
		"Land Acquisition",
		fields=[
			"name", "land_acquisition_title", "current_stage", "status",
			"land_location", "mouza", "dag", "area_katha", "area_bigha",
			"land_owner", "asking_price", "negotiated_price", "deal_value",
			"feasibility_score", "risk_rating", "legal_status",
			"litigation_check", "acquisition_date", "target_project",
			"priority", "next_action", "legal_checklist_progress",
		],
		order_by="modified desc",
		limit_page_length=200,
	)

	groups = {stage: [] for stage in STAGES}
	for r in records:
		stage = r.current_stage if r.current_stage in STAGES else "Lead"
		groups[stage].append(r)

	return {"stages": STAGES, "colors": STAGE_COLORS, "groups": groups, "total": len(records)}
