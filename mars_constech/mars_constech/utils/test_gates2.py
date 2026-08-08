import frappe

out = []


def t(label, fn):
	try:
		fn()
		out.append("PASS: " + label)
	except frappe.ValidationError as e:
		out.append("BLOCKED: " + label + " -> " + str(e)[:80])
	except Exception as e:
		out.append("FAIL: " + label + " -> " + type(e).__name__ + ": " + str(e)[:80])


la = frappe.new_doc("Land Acquisition")
la.land_acquisition_title = "Test Gate Record — Ashulia Plot"
la.land_location = "Ashulia, Savar"
la.land_owner = "Test Owner"
la.area_katha = 5.0
la.asking_price = 8000000
la.insert(ignore_permissions=True)
name = la.name
out.append("created " + name)


def skip_stage():
	d = frappe.get_doc("Land Acquisition", name)
	d.current_stage = "Negotiation"
	d.save(ignore_permissions=True)


t("skip DD (Lead->Negotiation) blocked", skip_stage)


def to_dd():
	d = frappe.get_doc("Land Acquisition", name)
	d.current_stage = "Due Diligence"
	d.save(ignore_permissions=True)


t("Lead->Due Diligence OK", to_dd)


def neg_blocked():
	d = frappe.get_doc("Land Acquisition", name)
	d.current_stage = "Negotiation"
	d.save(ignore_permissions=True)


t("DD->Negotiation w/ litigation Pending blocked", neg_blocked)


def neg_ok():
	d = frappe.get_doc("Land Acquisition", name)
	d.litigation_check = "Clear"
	d.khatian_cs = "CS 123"
	d.khatian_rs = "RS 67"
	d.current_stage = "Negotiation"
	d.save(ignore_permissions=True)


t("Negotiation after Clear + khatian OK", neg_ok)


def agree_blocked():
	d = frappe.get_doc("Land Acquisition", name)
	d.current_stage = "Agreement"
	d.save(ignore_permissions=True)


t("Neg->Agreement w/o price blocked", agree_blocked)


def agree_ok():
	d = frappe.get_doc("Land Acquisition", name)
	d.negotiated_price = 7500000
	d.deal_value = 7500000
	d.commission_pct = 1.5
	d.current_stage = "Agreement"
	d.save(ignore_permissions=True)


t("Agreement w/ price+commission OK", agree_ok)


def reg_blocked():
	d = frappe.get_doc("Land Acquisition", name)
	d.current_stage = "Registration"
	d.save(ignore_permissions=True)


t("Agreement->Registration w/o legal Cleared blocked", reg_blocked)


def reg_ok():
	d = frappe.get_doc("Land Acquisition", name)
	d.legal_status = "Cleared"
	d.append("documents", {"document_name": "Sale Deed", "document_type": "Sale Deed", "document_status": "Verified"})
	d.current_stage = "Registration"
	d.save(ignore_permissions=True)


t("Registration w/ legal+docs OK", reg_ok)


def poss_blocked():
	d = frappe.get_doc("Land Acquisition", name)
	d.current_stage = "Possession"
	d.save(ignore_permissions=True)


t("Reg->Possession w/o date blocked", poss_blocked)


def poss_ok():
	d = frappe.get_doc("Land Acquisition", name)
	d.acquisition_date = "2026-08-09"
	d.current_stage = "Possession"
	d.save(ignore_permissions=True)


t("Possession w/ date OK", poss_ok)

d = frappe.get_doc("Land Acquisition", name)
out.append("FINAL: " + d.current_stage + " | commission=" + str(d.commission_amount) + " | risk=" + str(d.risk_rating) + " | logs=" + str(len(d.stage_log)))

frappe.db.commit()
open("/tmp/gates3.out", "w").write("\n".join(out))
