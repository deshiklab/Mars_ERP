import frappe
from datetime import datetime

def get_context(context):
	context.now = datetime.now()
	context.no_cache = 1

	# live stats: projects, customers, bookings, units
	try:
		projects = frappe.db.get_all(
			"Project",
			filters={"status": ["in", ["Open", "Active", "Ongoing", "In Progress"]]},
			fields=["name", "project_name", "custom_location", "custom_total_units"],
			limit_page_length=6,
		)
	except Exception:
		projects = []

	# enrich projects with booked-unit counts from the REM bookings
	context.projects = []
	for p in projects:
		name = p.get("project_name") or p.get("name")
		booked = 0
		try:
			booked = frappe.db.count(
				"REM Booking",
				filters={"custom_project": ["like", f"%{name}%"]},
			)
		except Exception:
			pass
		context.projects.append({
			"name": name,
			"location": p.get("custom_location") or "",
			"total_units": p.get("custom_total_units") or "",
			"booked": booked or "",
			"status": p.get("status") or "Active",
		})

	# stats strip
	try:
		customers = frappe.db.count("Customer")
	except Exception:
		customers = 0
	try:
		bookings = frappe.db.count("REM Booking")
	except Exception:
		bookings = 0
	context.stats = [
		{"n": len(context.projects) or "—", "l": "Active Projects"},
		{"n": customers, "l": "Customers"},
		{"n": bookings, "l": "Bookings"},
		{"n": "12+", "l": "Years Experience"},
	]
