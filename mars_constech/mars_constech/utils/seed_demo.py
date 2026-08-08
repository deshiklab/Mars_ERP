# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt

import frappe


def seed_demo():
	"""Seed demo records for the Mars Constech doctypes (idempotent)."""
	if frappe.db.exists("Land Acquisition", "LA-00001"):
		frappe.db.commit()
		return "already seeded"

	# --- Land Acquisition with scorecard + legal checklist ---
	la = frappe.new_doc("Land Acquisition")
	la.land_acquisition_title = "Jolshiri Abason — Phase 1 Land"
	la.current_stage = "Negotiation"
	la.status = "In Progress"
	la.acquisition_date = "2026-06-01"
	la.land_location = "Jolshiri, Dhaka"
	la.area_katha = 12.5
	la.land_owner = "Delwar Hossain"
	la.seller_contact = "+880 1711-000000"
	la.asking_price = 25000000
	la.negotiated_price = 23500000
	la.deal_value = 23500000

	la.append(
		"scorecard",
		{
			"criterion": "Location & Access",
			"weight": 30,
			"score": 5,
			"remarks": "Prime location, road access confirmed",
		},
	)
	la.append(
		"scorecard",
		{
			"criterion": "Legal Title Clarity",
			"weight": 40,
			"score": 4,
			"remarks": "Mutation in progress",
		},
	)
	la.append(
		"scorecard",
		{
			"criterion": "Price vs Market",
			"weight": 20,
			"score": 4,
			"remarks": "5% below market",
		},
	)
	la.append(
		"scorecard",
		{
			"criterion": "Development Potential",
			"weight": 10,
			"score": 5,
			"remarks": "High-density zone",
		},
	)

	la.append(
		"legal_checklist",
		{
			"check_item": "Title Deed (Dokhila)",
			"required_document": "Original deed",
			"status": "Cleared",
		},
	)
	la.append(
		"legal_checklist",
		{
			"check_item": "Mutation Certificate",
			"required_document": "DC office",
			"status": "In Progress",
		},
	)
	la.append(
		"legal_checklist",
		{
			"check_item": "Tax Receipts (DCR)",
			"required_document": "City corporation",
			"status": "Cleared",
		},
	)
	la.append(
		"legal_checklist",
		{
			"check_item": "Encumbrance Certificate",
			"required_document": "Sub-registry",
			"status": "Pending",
		},
	)

	# audit trail: two prior stage transitions
	la.append("stage_log", {"stage": "Lead", "changed_on": "2026-05-10 10:00:00", "changed_by": "Kabir"})
	la.append("stage_log", {"stage": "Survey", "changed_on": "2026-05-25 14:30:00", "changed_by": "Kabir"})
	la.insert()

	# --- Project Lifecycle ---
	pl = frappe.new_doc("Project Lifecycle")
	pl.lifecycle_title = "Jolshiri Abason — Phase 1"
	pl.current_stage = "Land Acquisition"
	pl.status = "Active"
	pl.start_date = "2026-05-01"
	pl.expected_end_date = "2028-12-31"
	pl.progress_percent = 15
	pl.append("stage_transitions", {"stage": "Planning", "changed_on": "2026-05-01 09:00:00", "changed_by": "Kabir"})
	pl.insert()

	frappe.db.commit()
	return f"seeded: {la.name}, {pl.name}"
