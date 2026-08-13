import frappe
from frappe.model.document import Document

class REMProperty(Document):
	def autoname(self):
		# PRP-2026-0001 style naming
		if not self.property_name:
			year = frappe.utils.now_datetime().strftime("%Y")
			series = frappe.model.naming.make_autoname(f"PRP-{year}-.####", self)
			self.name = series
			self.property_name = series

	def validate(self):
		if self.size_sqft and self.sale_price and self.size_sqft > 0:
			self.price_per_sqft = round(float(self.sale_price) / float(self.size_sqft), 2)
