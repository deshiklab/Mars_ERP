# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe

STAGES = [
	"Lead",
	"Survey",
	"Negotiation",
	"Agreement",
	"Registration",
	"Handover",
]

STAGE_COLORS = {
	"Lead": "blue",
	"Survey": "cyan",
	"Negotiation": "orange",
	"Agreement": "purple",
	"Registration": "yellow",
	"Handover": "green",
}


@frappe.whitelist()
def get_pipeline():
	"""Return all Land Acquisition records grouped for the kanban."""
	records = frappe.get_all(
		"Land Acquisition",
		fields=[
			"name", "land_acquisition_title", "current_stage", "status",
			"land_location", "area_katha", "land_owner", "asking_price",
			"negotiated_price", "deal_value", "feasibility_score",
			"legal_status", "acquisition_date", "project",
		],
		order_by="modified desc",
		limit_page_length=200,
	)

	groups = {stage: [] for stage in STAGES}
	for r in records:
		stage = r.current_stage if r.current_stage in STAGES else "Lead"
		groups[stage].append(r)

	return {"stages": STAGES, "colors": STAGE_COLORS, "groups": groups, "total": len(records)}
