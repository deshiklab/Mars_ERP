# Copyright (c) 2026, MARS Constech and contributors
# For license information, please see license.txt
"""REM ERP server-sync bridge + portal actions.

Implements the API contract the V10 PWA expects (originally Flask). The PWA
calls <base>/login, <base>/bootstrap, <base>/sync, <base>/logout where base is
set in Settings -> Server Sync to:

    http://localhost:8000/api/method/mars_constech.mars_constech.api

So each method below must be directly addressable as
mars_constech.mars_constech.api.<method> — hence they live here, not in a
submodule (Frappe resolves the last dotted segment as the function name).

Collections are stored 1:1 as JSON blobs in the "REM Collection" doctype so the
PWA keeps working unchanged. Core modules (Booking, Land Acquisition, Project
Lifecycle) additionally have real doctypes.
"""

import json

import frappe
from frappe import _

REM_COLLECTION_DOCTYPE = "REM Collection"


@frappe.whitelist(allow_guest=True)
def login(usr=None, pwd=None, email=None, password=None):
	"""Login and mint a token. Accepts both (usr/pwd) and (email/password) forms."""
	user = usr or email
	passwd = pwd or password
	if not user or not passwd:
		frappe.throw(_("Email and password required"), frappe.AuthenticationError)

	try:
		frappe.local.login_manager = frappe.auth.LoginManager()
		frappe.local.login_manager.authenticate(user=user, pwd=passwd)
		frappe.local.login_manager.post_login()
	except frappe.exceptions.AuthenticationError:
		frappe.throw(_("Invalid login"), frappe.AuthenticationError)

	token = frappe.local.session.sid if frappe.local.session else frappe.session.sid
	frappe.db.commit()
	# Track last connected user server-side (REM Settings) so other browsers see it.
	try:
		doc = frappe.get_single("REM Settings")
		doc.last_connected_user = user
		doc.last_sync_time = frappe.utils.now()
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
	return {
		"token": token,
		"full_name": frappe.utils.get_fullname(user),
		"user": user,
		"session_expiry": _session_expiry_hint(),
	}


@frappe.whitelist()
def logout():
	frappe.local.login_manager.logout()
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def bootstrap():
	"""Return every stored collection, mirroring the PWA's localStorage keys."""
	collections = {}
	rows = frappe.get_all(
		REM_COLLECTION_DOCTYPE,
		fields=["collection_key", "json_data"],
		limit_page_length=500,
	)
	for r in rows:
		try:
			collections[r.collection_key] = json.loads(r.json_data or "[]")
		except Exception:
			collections[r.collection_key] = []
	return {
		"collections": collections,
		"meta": {
			"server_time": frappe.utils.now(),
			"source": "frappe",
			"pwa_version": _rem_settings().get("pwa_version", "2.0.0"),
			"settings": _rem_settings(),
			"session_expiry": _session_expiry_hint(),
			"user": frappe.session.user,
		},
	}


@frappe.whitelist()
def sync(collections=None):
	"""Upsert collections pushed from the PWA. Returns row counts."""
	if not collections:
		collections = {}
	if not isinstance(collections, dict):
		frappe.throw(_("collections must be an object"), frappe.ValidationError)

	total = 0
	for key, data in collections.items():
		if key.startswith("_") or not isinstance(data, (list, dict)):
			continue
		payload = json.dumps(data, ensure_ascii=False, default=str)
		existing = frappe.db.exists(REM_COLLECTION_DOCTYPE, key)
		if existing:
			doc = frappe.get_doc(REM_COLLECTION_DOCTYPE, existing)
		else:
			doc = frappe.new_doc(REM_COLLECTION_DOCTYPE)
			doc.collection_key = key
		doc.json_data = payload
		doc.record_count = len(data) if isinstance(data, list) else 1
		doc.last_updated = frappe.utils.now()
		doc.flags.ignore_permissions = True
		doc.save(ignore_permissions=True)
		total += doc.record_count

	frappe.db.commit()
	return {"rows": total, "collections": len(collections)}


# --------------------------------------------------------------------------
# Portal actions
# --------------------------------------------------------------------------
def _portal_customer():
	"""Resolve the portal user's Customer (via User Permission)."""
	perms = frappe.get_all(
		"User Permission",
		filters={"user": frappe.session.user, "allow": "Customer"},
		fields=["for_value"],
		limit=1,
	)
	return perms[0].for_value if perms else None


def _owns_invoice(invoice_name):
	"""Portal user must own the invoice."""
	customer = _portal_customer()
	if not customer:
		return False
	inv = frappe.get_doc("Sales Invoice", invoice_name)
	return inv.customer == customer


@frappe.whitelist()
def download_invoice(invoice_name):
	"""Stream the MARS-branded invoice PDF (portal users: own invoices only)."""
	if not _owns_invoice(invoice_name):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	from frappe.utils.print_format import download_pdf

	# download_pdf sets frappe.local.response (filename/filecontent/type) itself
	download_pdf("Sales Invoice", invoice_name, "MARS Sales Invoice")
	return None


@frappe.whitelist()
def pay_invoice(invoice_name, gateway="bkash"):
	"""Start payment for an invoice. Returns {redirect, payment_id}."""
	if not _owns_invoice(invoice_name):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	from mars_constech.mars_constech.payments.gateways import create_payment

	return create_payment(invoice_name, gateway)


@frappe.whitelist(allow_guest=True)
def payment_callback(gateway=None, payment_id=None, invoice=None, amount=None, **kwargs):
	"""Gateway callback: verify + settle. Also used by the demo payment page."""
	if not gateway:
		gateway = kwargs.get("gateway") or frappe.form_dict.get("gateway")
	if not payment_id:
		payment_id = kwargs.get("paymentID") or frappe.form_dict.get("paymentID")
	if not invoice:
		invoice = kwargs.get("invoice") or frappe.form_dict.get("invoice")

	from mars_constech.mars_constech.payments.gateways import verify_and_settle

	ok, message, pe = verify_and_settle(gateway, payment_id, invoice, amount)
	if not ok:
		frappe.local.message = message
		frappe.local.response.message = message
		return {"ok": False, "message": message}
	return {"ok": True, "message": message, "payment_entry": pe}


@frappe.whitelist(allow_guest=True)
def demo_confirm(ref=None, **kwargs):
	"""Demo-mode confirm: mark the simulated payment as completed."""
	if not ref:
		ref = kwargs.get("ref") or frappe.form_dict.get("ref")
	if not ref:
		frappe.throw(_("Missing ref"), frappe.ValidationError)
	rec = frappe.cache().get_value(f"mars_demo_pay_{ref}")
	if not rec:
		return {"ok": False, "message": _("Payment session not found or expired")}

	from mars_constech.mars_constech.payments.gateways import verify_and_settle

	ok, message, pe = verify_and_settle(rec["gateway"].lower(), ref)
	return {"ok": ok, "message": message, "payment_entry": pe}


# --------------------------------------------------------------------------
# Land Acquisition pipeline (C milestone): PWA <-> real doctype
# --------------------------------------------------------------------------
# Stage mapping: doctype uses "Lead"/"Due Diligence"/... ; the V10 PWA uses
# identification/due_diligence/negotiation/agreement/registration/possession.
PWA_STAGE_MAP = {
    "Lead": "identification",
    "Due Diligence": "due_diligence",
    "Negotiation": "negotiation",
    "Agreement": "agreement",
    "Registration": "registration",
    "Possession": "possession",
}
DOCTYPE_STAGE_MAP = {v: k for k, v in PWA_STAGE_MAP.items()}


def parse_bdt(s):
	"""Parse PWA money strings to a BDT number: '৳1.8 Cr', '৳46.0L', '৳10,00,000'."""
	if s is None:
		return 0
	s = str(s).replace("৳", "").replace(",", "").strip()
	if not s:
		return 0
	try:
		if s.lower().endswith("cr"):
			return int(float(s[:-2]) * 10000000)
		if s.lower().endswith("l") and not s.lower().endswith("la"):
			return int(float(s[:-1]) * 100000)
		return int(float(s))
	except Exception:
		return 0


def _fmt_bdt(value):
    """BDT number -> PWA-friendly string (Cr / Lac / plain)."""
    if not value:
        return "৳ 0"
    v = float(value)
    if v >= 10000000:
        return "৳ {0:.1f} Cr".format(v / 10000000)
    if v >= 100000:
        return "৳ {0:.1f} Lac".format(v / 100000)
    return "৳ {0:,.0f}".format(v)


def _la_to_pwa(la):
    """Map a Land Acquisition doctype doc to the PWA's land_proposals shape."""
    owners = [
        {"name": o.owner_name, "share": str(o.share_pct or "") + "%"}
        for o in (la.get("owners") or [])
        if o.get("owner_name")
    ]
    docs = [
        {"name": d.document_name, "type": d.document_type or "Doc", "status": d.document_status or "Pending"}
        for d in (la.get("documents") or [])
        if d.get("document_name")
    ]
    deal = la.deal_value or la.negotiated_price or la.asking_price or 0
    area = ""
    if la.get("area_bigha"):
        area = "{0} Bigha".format(la.area_bigha)
    elif la.get("area_katha"):
        area = "{0} Katha".format(la.area_katha)
    return {
        "id": la.name,
        "name": la.land_acquisition_title,
        "location": la.land_location or "",
        "stage": PWA_STAGE_MAP.get(la.current_stage, la.current_stage or "identification"),
        "status": la.status or "Open",
        "risk": la.risk_rating or "Low",
        "priority": la.priority or "Medium",
        "price": deal,
        "priceF": _fmt_bdt(deal),
        "area": area,
        "roi": ("{0}%".format(la.estimated_roi) if la.get("estimated_roi") else ""),
        "progress": la.legal_checklist_progress or la.feasibility_score or 0,
        "legalStatus": la.legal_status or "Pending",
        "legalItems": len(la.get("legal_checklist") or []),
        "nextAction": la.next_action or "",
        "archived": la.status in ("Closed", "Rejected"),
        "owners": owners,
        "documents": docs,
        "mouza": la.mouza or "",
        "dag": ("Dag {0}".format(la.dag) if la.get("dag") else ""),
        "cs": ("CS {0}".format(la.khatian_cs) if la.get("khatian_cs") else ""),
        "rs": ("RS {0}".format(la.khatian_rs) if la.get("khatian_rs") else ""),
        "commission": ("{0}%".format(la.commission_pct) if la.get("commission_pct") else ""),
        "roadAccess": la.road_access or "",
        "landUse": la.land_use or "",
        "soilCondition": la.soil_condition or "",
        "floodRisk": la.flood_risk or "Low",
        "litigationCheck": la.litigation_check or "Pending",
        "landmarks": la.landmarks or "",
        "coordinates": la.coordinates or "",
        "targetProject": la.target_project or "",
        "expectedRevenue": la.expected_revenue or 0,
        "totalCost": la.total_project_cost or 0,
        "netProfit": la.net_profit_est or 0,
        "mutationStatus": la.mutation_status or "Not Started",
        "feasibilityStatus": la.feasibility_status or "Pending Visit",
        "surveyStatus": la.survey_status or "Pending",
        "rajukStatus": la.rajuk_status or "Not Required",
        "envClearanceStatus": la.env_clearance_status or "Not Required",
        "layoutStatus": la.layout_status or "Not Started",
    }


@frappe.whitelist()
def land_pipeline():
    """Return every Land Acquisition record in the PWA's land_proposals shape."""
    rows = frappe.get_all(
        "Land Acquisition",
        fields=[
            "name", "land_acquisition_title", "current_stage", "status",
            "land_location", "mouza", "dag", "khatian_cs", "khatian_sa",
            "khatian_rs", "area_katha", "area_bigha", "priority", "next_action",
            "asking_price", "negotiated_price", "deal_value", "commission_pct",
            "estimated_roi", "risk_rating", "legal_checklist_progress",
            "feasibility_score", "litigation_check", "flood_risk", "road_access",
            "land_use", "soil_condition", "landmarks", "coordinates",
            "target_project", "expected_revenue", "total_project_cost",
            "net_profit_est", "mutation_status", "feasibility_status",
            "survey_status", "rajuk_status", "env_clearance_status",
            "layout_status", "acquisition_date",
        ],
        order_by="modified desc",
        limit_page_length=500,
    )
    proposals = []
    for r in rows:
        la = frappe.get_doc("Land Acquisition", r.name)
        proposals.append(_la_to_pwa(la))
    return {"proposals": proposals, "count": len(proposals)}


@frappe.whitelist()
def land_sync(proposals=None):
    """Upsert proposals pushed from the PWA into the Land Acquisition doctype.

    Each proposal must carry a Frappe name (id starts with 'LA-') to update an
    existing record; otherwise a new record is created with the mapped stage.
    Returns {created, updated, errors}.
    """
    if not proposals:
        return {"created": 0, "updated": 0, "errors": []}
    if not isinstance(proposals, list):
        frappe.throw(_("proposals must be a list"), frappe.ValidationError)

    created = updated = 0
    errors = []
    for p in proposals:
        try:
            if not isinstance(p, dict) or not p.get("name"):
                continue
            name = p.get("id") or ""
            stage = DOCTYPE_STAGE_MAP.get(p.get("stage"), "Lead")
            payload = {
                "land_acquisition_title": p.get("name"),
                "land_location": p.get("location"),
                "current_stage": stage,
                "status": p.get("status") or "Open",
                "mouza": p.get("mouza"),
                "priority": p.get("priority") or "Medium",
                "risk_rating": p.get("risk") or "Low",
                "next_action": p.get("nextAction"),
            }
            if name.startswith("LA-") and frappe.db.exists("Land Acquisition", name):
                doc = frappe.get_doc("Land Acquisition", name)
                for f, v in payload.items():
                    if v not in (None, ""):
                        doc.set(f, v)
                doc.flags.ignore_permissions = True
                doc.save(ignore_permissions=True)
                updated += 1
            else:
                doc = frappe.new_doc("Land Acquisition")
                for f, v in payload.items():
                    if v not in (None, ""):
                        doc.set(f, v)
                doc.flags.ignore_permissions = True
                doc.insert(ignore_permissions=True)
                created += 1
        except Exception as e:
            errors.append({"name": p.get("name"), "error": str(e)})
    frappe.db.commit()
    return {"created": created, "updated": updated, "errors": errors}
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Legal team feedback (PWA Legal Vetting tab)
# --------------------------------------------------------------------------
LEGAL_STATUSES = ["Pending", "Received", "Verified", "Issues Found", "Not Applicable"]


@frappe.whitelist()
def land_legal_checklist(name=None):
    """Fetch the legal checklist (child rows) + progress for one Land Acquisition."""
    if not name:
        frappe.throw(_("Missing name"), frappe.ValidationError)
    if not frappe.db.exists("Land Acquisition", name):
        return {"items": [], "progress": 0, "legal_status": "Pending", "error": "not found"}
    la = frappe.get_doc("Land Acquisition", name)
    items = []
    for row in (la.get("legal_checklist") or []):
        items.append({
            "check_item": row.check_item,
            "is_required": row.is_required,
            "status": row.status or "Pending",
            "document_ref": row.document_ref or "",
            "verified_by": row.verified_by or "",
            "verified_on": str(row.verified_on) if row.verified_on else "",
            "remarks": row.remarks or "",
        })
    return {
        "items": items,
        "progress": la.legal_checklist_progress or 0,
        "legal_status": la.legal_status or "Pending",
        "stage": la.current_stage or "Lead",
        "count": len(items),
    }


@frappe.whitelist()
def land_legal_update(name=None, items=None):
    """Save legal team feedback back to the doctype legal_checklist child table.

    items: [{"check_item": "...", "status": "Verified", "document_ref": "...",
             "remarks": "..."}]
    Only fields the legal team can set are accepted; verified_by/verified_on are
    stamped server-side from the current user. Returns updated progress.
    """
    if not name:
        frappe.throw(_("Missing name"), frappe.ValidationError)
    if not items or not isinstance(items, list):
        frappe.throw(_("items must be a list"), frappe.ValidationError)
    if not frappe.db.exists("Land Acquisition", name):
        frappe.throw(_("Land Acquisition {0} not found").format(name), frappe.ValidationError)

    la = frappe.get_doc("Land Acquisition", name)
    # map existing rows by check_item
    by_item = {}
    for row in (la.get("legal_checklist") or []):
        by_item[row.check_item] = row

    for it in items:
        if not isinstance(it, dict) or not it.get("check_item"):
            continue
        ci = it["check_item"]
        row = by_item.get(ci)
        if not row:
            continue  # never create rows from PWA; use Load Standard Checklist server-side
        status = it.get("status") or row.status or "Pending"
        if status not in LEGAL_STATUSES:
            frappe.throw(_("Invalid status {0} for {1}").format(status, ci), frappe.ValidationError)
        row.status = status
        if it.get("document_ref") is not None:
            row.document_ref = it["document_ref"]
        if it.get("remarks") is not None:
            row.remarks = it["remarks"]
        if status == "Verified" or status == "Issues Found":
            row.verified_by = frappe.session.user
            row.verified_on = frappe.utils.today()
        elif status == "Received":
            row.verified_by = ""
            row.verified_on = None

    # recompute progress (mirror controller: Verified + N/A count / required total)
    total = 0
    done = 0
    for row in (la.get("legal_checklist") or []):
        if row.is_required:
            total += 1
            if row.status in ("Verified", "Not Applicable"):
                done += 1
    la.legal_checklist_progress = round(done * 100.0 / total, 1) if total else 0
    la.flags.ignore_permissions = True
    la.save(ignore_permissions=True)
    frappe.db.commit()
    return {
        "ok": True,
        "progress": la.legal_checklist_progress,
        "legal_status": la.legal_status or "Pending",
        "updated": len(items),
    }


@frappe.whitelist()
def land_legal_load_standard(name=None):
    """Load the standard 14-item checklist into a record if empty (mirrors form button)."""
    if not name:
        frappe.throw(_("Missing name"), frappe.ValidationError)
    if not frappe.db.exists("Land Acquisition", name):
        frappe.throw(_("Land Acquisition {0} not found").format(name), frappe.ValidationError)
    la = frappe.get_doc("Land Acquisition", name)
    from mars_constech.mars_constech.doctype.land_acquisition.land_acquisition import (
        STANDARD_LEGAL_CHECKLIST,
    )
    if la.get("legal_checklist"):
        return {"ok": True, "loaded": 0, "message": "Checklist already present"}
    for item, req, _desc in STANDARD_LEGAL_CHECKLIST:
        la.append(
            "legal_checklist",
            {
                "check_item": item,
                "is_required": 1 if req else 0,
                "status": "Pending",
            },
        )
    la.flags.ignore_permissions = True
    la.save(ignore_permissions=True)
    frappe.db.commit()
    return {"ok": True, "loaded": len(STANDARD_LEGAL_CHECKLIST), "progress": 0}
# --------------------------------------------------------------------------
# Friendly index for the API base URL (avoids the bare-path 500)
# --------------------------------------------------------------------------



# ═══ LEADS BRIDGE (PWA CRM & Leads → ERPNext Lead) ═══

LEAD_FUNNEL = ["New Inquiry", "Site Visit", "Negotiation", "Booking", "Downpayment", "Installments", "Converted", "Lost"]

def _lead_to_pwa(lead):
	"""Map a native Lead doctype record to the PWA lead field contract."""
	return {
		"id": lead.custom_rem_ref or ("LD-" + str(lead.name)),
		"name": lead.lead_name or "",
		"territory": lead.territory or "",
		"phone": lead.phone or "",
		"email": lead.email_id or "",
		"property": lead.custom_rem_property or "",
		"status": lead.custom_rem_status or "New Inquiry",
		"priority": "Medium",
		"type": lead.type or "Local",
		"source": lead.source or "",
		"value": _fmt_bdt(lead.custom_rem_value or 0),
		"owner": lead.lead_owner or "",
		"lastContact": "",
		"nextFollowUp": "",
		"notes": "",
	}


@frappe.whitelist()
def leads_pipeline():
	"""Pull all leads (native Lead doctype) in the PWA contract."""
	rows = frappe.get_all(
		"Lead",
		fields=["name", "lead_name", "custom_rem_ref", "custom_rem_status", "status",
				"territory", "phone", "email_id", "custom_rem_property", "custom_rem_value",
				"type", "source", "lead_owner"],
		order_by="creation desc",
		limit_page_length=500,
	)
	out = [_lead_to_pwa(r) for r in rows]
	return {"count": len(out), "leads": out}


@frappe.whitelist()
def leads_sync(leads=None):
	"""Upsert leads pushed from the PWA into the native Lead doctype.

	Dedupe via custom_rem_ref (PWA id) when present; otherwise by email.
	"""
	if not leads or not isinstance(leads, list):
		frappe.throw(_("leads must be a list"), frappe.ValidationError)
	created = updated = 0
	for item in leads:
		if not isinstance(item, dict) or not item.get("name"):
			continue
		existing = None
		if item.get("id") and str(item["id"]).startswith("LD-"):
			existing = frappe.db.get_value("Lead", {"custom_rem_ref": str(item["id"])})
		if not existing and item.get("email"):
			existing = frappe.db.get_value("Lead", {"email_id": item["email"]})
		doc = frappe.get_doc("Lead", existing) if existing else frappe.new_doc("Lead")
		doc.flags.ignore_permissions = True
		doc.lead_name = str(item["name"])[:140]
		doc.custom_rem_ref = str(item.get("id") or "")
		doc.custom_rem_status = str(item.get("status") or "New Inquiry")
		doc.custom_rem_property = str(item.get("property") or "")
		doc.phone = str(item.get("phone") or "")
		doc.email_id = str(item.get("email") or "")
		doc.territory = str(item.get("territory") or "")
		doc.source = str(item.get("source") or "")
		doc.lead_type = str(item.get("type") or "Local")
		if item.get("value"):
			try:
				doc.custom_rem_value = parse_bdt(str(item["value"]))
			except Exception:
				pass
		doc.notes = str(item.get("notes") or "")
		if existing:
			doc.save()
			updated += 1
		else:
			doc.insert()
			created += 1
	frappe.db.commit()
	return {"created": created, "updated": updated}


@frappe.whitelist()
def lead_update_status(name=None, status=None):
	"""Set the REM funnel status on a lead."""
	if not name or status not in LEAD_FUNNEL:
		frappe.throw(_("Invalid lead/status"), frappe.ValidationError)
	doc = frappe.get_doc("Lead", name)
	doc.custom_rem_status = status
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return _lead_to_pwa(doc)



# ═══ BOOKINGS BRIDGE (PWA Bookings → REM Booking doctype) ═══

BOOKING_STAGES = ["Pending Review", "Pending Approval", "Confirmed", "Delivered", "Cancelled"]


def _booking_to_pwa(b):
	"""Map a REM Booking record to the PWA booking field contract."""
	inst = []
	for i in b.get("installments") or []:
		inst.append({"no": i.installment_no, "date": str(i.due_date or ""), "amount": i.amount or 0, "status": i.status or "Upcoming"})
	return {
		"id": b.custom_booking_ref or b.name,
		"client": b.customer_name or "",
		"date": str(b.creation or "")[:10],
		"property": b.project_name or "",
		"unit": b.unit or "",
		"price": _fmt_bdt(b.deal_value or 0),
		"advance": _fmt_bdt(b.advance_paid or 0),
		"status": b.status or "Pending Review",
		"type": b.booking_type or "Flat",
		"terms": b.payment_terms or "",
		"schedStart": str(b.schedule_start or ""),
		"total_paid": b.total_paid or 0,
		"total_due": b.total_due or 0,
		"installments": inst,
		"sales_invoice": b.sales_invoice or "",
		"payment_entry": b.payment_entry or "",
		"name": b.name,
	}


@frappe.whitelist()
def bookings_pipeline():
	"""Pull all REM Bookings in the PWA contract (incl. payment schedule)."""
	rows = frappe.get_all(
		"REM Booking",
		fields=["name", "custom_booking_ref", "customer_name", "project_name", "unit",
				"booking_type", "deal_value", "advance_paid", "payment_terms", "schedule_start",
				"status", "total_paid", "total_due", "sales_invoice", "payment_entry", "creation"],
		order_by="creation desc",
		limit_page_length=500,
	)
	out = []
	for r in rows:
		doc = frappe.get_doc("REM Booking", r.name)
		out.append(_booking_to_pwa(doc))
	return {"count": len(out), "bookings": out}


@frappe.whitelist()
def bookings_sync(bookings=None):
	"""Upsert bookings pushed from the PWA (dedupe via custom_booking_ref)."""
	if not bookings or not isinstance(bookings, list):
		frappe.throw(_("bookings must be a list"), frappe.ValidationError)
	created = updated = 0
	for item in bookings:
		if not isinstance(item, dict) or not item.get("client"):
			continue
		existing = None
		if item.get("id"):
			existing = frappe.db.get_value("REM Booking", {"custom_booking_ref": str(item["id"])})
		doc = frappe.get_doc("REM Booking", existing) if existing else frappe.new_doc("REM Booking")
		doc.flags.ignore_permissions = True
		doc.custom_booking_ref = str(item.get("id") or "")
		doc.customer_name = str(item.get("client") or "")[:140]
		doc.project_name = str(item.get("property") or "")
		doc.unit = str(item.get("unit") or "")
		doc.booking_type = str(item.get("type") or "Flat")
		doc.payment_terms = str(item.get("terms") or "")
		if item.get("scheduleStart"):
			try:
				doc.schedule_start = str(item["scheduleStart"])[:10]
			except Exception:
				pass
		doc.deal_value = parse_bdt(item.get("price"))
		doc.advance_paid = parse_bdt(item.get("advance"))
		st = str(item.get("status") or "Pending Review")
		doc.status = st if st in BOOKING_STAGES else "Pending Review"
		# installments child
		doc.installments = []
		for i in (item.get("installments") or []):
			doc.append("installments", {
				"installment_no": i.get("no") or 0,
				"due_date": str(i.get("date") or "")[:10],
				"amount": i.get("amount") or 0,
				"status": str(i.get("status") or "Upcoming"),
			})
		if existing:
			doc.save()
			updated += 1
		else:
			doc.insert()
			created += 1
	frappe.db.commit()
	return {"created": created, "updated": updated}


@frappe.whitelist()
def booking_update_status(name=None, status=None):
	"""Set booking status (stage gate: Confirmed requires advance >= 10% of deal)."""
	if not name or status not in BOOKING_STAGES:
		frappe.throw(_("Invalid booking/status"), frappe.ValidationError)
	doc = frappe.get_doc("REM Booking", name)
	if status == "Confirmed":
		deal = doc.deal_value or 0
		adv = doc.advance_paid or 0
		if deal > 0 and adv < deal * 0.10:
			frappe.throw(_("Cannot confirm: advance must be at least 10% of deal value"), frappe.ValidationError)
	doc.status = status
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return _booking_to_pwa(doc)



# ═══ BOOKING → INVOICE / PAYMENT (native ERPNext) ═══

def _get_company():
	"""Default company (for invoice/payment creation)."""
	try:
		return frappe.db.get_single_value("Global Defaults", "default_company") or 			(frappe.get_all("Company", limit=1) or [{}])[0].get("name", "")
	except Exception:
		return ""


def _get_or_create_customer(booking):
	"""Find or create a Customer for the booking's client name."""
	name = booking.customer_name or ""
	if not name:
		frappe.throw(_("Booking has no customer name"), frappe.ValidationError)
	# existing by name
	existing = frappe.db.get_value("Customer", {"customer_name": name})
	if existing:
		return existing
	# or by linked lead/customer on the booking
	if booking.customer:
		return booking.customer
	# pick a NON-GROUP customer group (group-type groups are rejected on save)
	cg = frappe.db.get_value("Customer Group", {"is_group": 0, "name": "Individual"}, "name") \
		or frappe.db.get_value("Customer Group", {"is_group": 0}, "name") \
		or "Individual"
	doc = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": name[:140],
		"customer_group": cg,
		"territory": "All Territories",
	})
	doc.flags.ignore_permissions = True
	doc.insert()
	return doc.name


def _get_sales_item():
	"""Default sellable item for the booked unit (create once if missing)."""
	item = frappe.db.get_value("Item", {"item_name": "Booked Unit"})
	if item:
		return item
	company = _get_company()
	income_acct = frappe.db.get_value("Account", {"account_type": "Income", "company": company, "is_group": 0}, "name")
	doc = frappe.get_doc({
		"doctype": "Item",
		"item_code": "REM-BOOKED-UNIT",
		"item_name": "Booked Unit",
		"item_group": "All Item Groups",
		"stock_uom": "Nos",
		"is_stock_item": 0,
		"income_account": income_acct or "",
	})
	doc.flags.ignore_permissions = True
	doc.insert()
	return doc.name


@frappe.whitelist()
def booking_invoice(name=None, amount=None):
	"""Create a native Sales Invoice for a booking (default: full deal value)."""
	if not name:
		frappe.throw(_("booking name required"), frappe.ValidationError)
	doc = frappe.get_doc("REM Booking", name)
	company = _get_company()
	if not company:
		frappe.throw(_("No default company configured — set Global Defaults"), frappe.ValidationError)
	customer = _get_or_create_customer(doc)
	item = _get_sales_item()
	amt = float(amount or doc.deal_value or 0)
	if amt <= 0:
		frappe.throw(_("Invoice amount must be positive"), frappe.ValidationError)
	recv_acct = frappe.db.get_value("Account", {"account_type": "Receivable", "company": company, "is_group": 0}, "name")
	sinv = frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": customer,
		"company": company,
		"due_date": frappe.utils.today(),
		"debit_to": recv_acct or "",
		"items": [{"item_code": item, "qty": 1, "rate": amt, "description": f"{doc.project_name or ''} {doc.unit or ''} — {doc.customer_name or ''}"}],
	})
	sinv.flags.ignore_permissions = True
	sinv.flags.ignore_mandatory = True
	# account-selection permission checks are bypassed by running as Administrator
	frappe.set_user("Administrator")
	try:
		sinv.insert()
		sinv.submit()
	finally:
		frappe.set_user(frappe.session.user)
	doc.sales_invoice = sinv.name
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"invoice": sinv.name, "amount": amt, "customer": customer, "grand_total": sinv.grand_total}


@frappe.whitelist()
def booking_payment(name=None, amount=None, mode_of_payment="Cash", reference_no=None):
	"""Record a Payment Entry against the booking's Sales Invoice."""
	if not name:
		frappe.throw(_("booking name required"), frappe.ValidationError)
	doc = frappe.get_doc("REM Booking", name)
	sinv = doc.sales_invoice
	if not sinv:
		# auto-create invoice for the payment amount
		inv = booking_invoice(name=name, amount=amount)
		sinv = inv["invoice"]
	company = _get_company()
	customer = _get_or_create_customer(doc)
	amt = float(amount or 0)
	if amt <= 0:
		frappe.throw(_("Payment amount must be positive"), frappe.ValidationError)
	# fall back to an existing Mode of Payment if the requested one is unknown
	if not frappe.db.exists("Mode of Payment", mode_of_payment):
		mode_of_payment = frappe.db.get_value("Mode of Payment", {}, "name") or "Cash"
	recv_acct = frappe.db.get_value("Account", {"account_type": "Receivable", "company": company, "is_group": 0}, "name")
	bank_acct = frappe.db.get_value("Company", company, "default_bank_account") or \
		frappe.db.get_value("Account", {"account_type": "Bank", "company": company, "is_group": 0}, "name") or \
		frappe.db.get_value("Account", {"account_type": "Cash", "company": company, "is_group": 0}, "name") or \
		frappe.db.get_value("Account", {"company": company, "is_group": 0}, "name") or ""
	# For payment_type "Receive": paid_from = the party (Receivable) account,
	# paid_to = the Bank/Cash account the money lands in. (Reversed accounts
	# make GL entries for the Receivable account lose their party → 417.)
	pe = frappe.get_doc({
		"doctype": "Payment Entry",
		"payment_type": "Receive",
		"party_type": "Customer",
		"party": customer,
		"company": company,
		"paid_from": recv_acct or "",
		"paid_to": bank_acct,
		"paid_from_account_currency": frappe.db.get_value("Account", recv_acct, "account_currency") if recv_acct else "BDT",
		"paid_to_account_currency": frappe.db.get_value("Account", bank_acct, "account_currency") if bank_acct else "BDT",
		"target_exchange_rate": 1,
		"source_exchange_rate": 1,
		"paid_amount": amt,
		"received_amount": amt,
		"mode_of_payment": mode_of_payment,
		"reference_no": reference_no or "",
		"references": [{"reference_doctype": "Sales Invoice", "reference_name": sinv, "allocated_amount": amt}],
	})
	pe.flags.ignore_permissions = True
	pe.flags.ignore_mandatory = True
	frappe.set_user("Administrator")
	try:
		pe.insert()
		pe.submit()
	finally:
		frappe.set_user(frappe.session.user)
	doc.payment_entry = pe.name
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"payment_entry": pe.name, "invoice": sinv, "amount": amt}



# ═══ PROJECTS & TASKS BRIDGE (PWA Projects/Tasks → ERPNext Project/Task) ═══

PROJECT_STAGES = ["Planning", "In Progress", "Near Completion", "Completed", "On Hold"]


def _project_to_pwa(pj):
	"""Map a native Project to the PWA project contract."""
	return {
		"id": pj.custom_rem_ref or ("P-" + str(pj.name)),
		"name": pj.project_name or "",
		"type": pj.custom_rem_type or "land",
		"location": "",
		"status": _pj_stage(pj.status) or "Planning",
		"progress": pj.custom_rem_progress or 0,
		"budget": _fmt_bdt(pj.custom_rem_budget or 0),
		"manager": "",
		"plots": pj.custom_rem_plots or 0,
		"start": str(pj.expected_start_date or "")[:7],
		"end": str(pj.expected_end_date or "")[:7],
		"phase": pj.custom_rem_phase or "",
		"desc": pj.notes or "",
		"milestones": [],
		"la_ref": pj.custom_rem_la_ref or "",
	}


def _pj_stage(status):
	"""Map ERPNext Project.status to REM stage names."""
	m = {"Open": "In Progress", "In Progress": "In Progress", "Completed": "Completed", "Cancelled": "On Hold"}
	return m.get(status or "", "")


@frappe.whitelist()
def projects_pipeline():
	"""Pull all Projects in the PWA contract."""
	rows = frappe.get_all(
		"Project",
		fields=["name", "project_name", "custom_rem_ref", "custom_rem_type", "custom_rem_progress",
				"custom_rem_plots", "custom_rem_phase", "custom_rem_budget", "custom_rem_la_ref",
				"status", "expected_start_date", "expected_end_date", "notes"],
		order_by="creation desc",
		limit_page_length=500,
	)
	return {"count": len(rows), "projects": [_project_to_pwa(r) for r in rows]}


@frappe.whitelist()
def projects_sync(projects=None):
	"""Upsert projects pushed from the PWA (dedupe via custom_rem_ref)."""
	if not projects or not isinstance(projects, list):
		frappe.throw(_("projects must be a list"), frappe.ValidationError)
	created = updated = 0
	for item in projects:
		if not isinstance(item, dict) or not item.get("name"):
			continue
		existing = None
		if item.get("id"):
			existing = frappe.db.get_value("Project", {"custom_rem_ref": str(item["id"])})
		if not existing and item.get("name"):
			# Project.project_name is unique — dedupe by name too (covers
			# projects already created via land-acquisition merge)
			existing = frappe.db.get_value("Project", {"project_name": str(item["name"])})
		doc = frappe.get_doc("Project", existing) if existing else frappe.new_doc("Project")
		doc.flags.ignore_permissions = True
		doc.project_name = str(item.get("name") or "")[:140]
		doc.custom_rem_ref = str(item.get("id") or "")
		doc.custom_rem_type = str(item.get("type") or "land")
		doc.custom_rem_progress = int(item.get("progress") or 0)
		doc.custom_rem_plots = int(item.get("plots") or 0)
		doc.custom_rem_phase = str(item.get("phase") or "")
		doc.custom_rem_la_ref = str(item.get("la_ref") or "")
		doc.custom_rem_budget = parse_bdt(item.get("budget"))
		doc.notes = str(item.get("desc") or "")
		if existing:
			doc.save()
			updated += 1
		else:
			doc.insert()
			created += 1
	frappe.db.commit()
	return {"created": created, "updated": updated}


def _task_to_pwa(t):
	"""Map a native Task to the PWA task contract."""
	return {
		"id": t.custom_rem_ref or t.name,
		"title": t.subject or "",
		"status": {"Open": "To Do", "Working": "In Progress", "Completed": "Done", "Cancelled": "Blocked", "Overdue": "In Progress"}.get(t.status or "", t.status or "To Do"),
		"priority": t.custom_rem_priority or t.priority or "Medium",
		"project": t.project or "",
		"assignee": t._assign or "",
		"deadline": str(t.exp_start_date or "")[:10],
		"desc": t.description or "",
		"tags": [],
		"name": t.name,
	}


@frappe.whitelist()
def tasks_pipeline(project=None):
	"""Pull tasks (optionally filtered by project)."""
	filters = {}
	if project:
		filters["project"] = project
	rows = frappe.get_all(
		"Task",
		filters=filters,
		fields=["name", "subject", "status", "priority", "custom_rem_priority", "custom_rem_ref",
				"project", "_assign", "exp_start_date", "description"],
		order_by="creation desc",
		limit_page_length=500,
	)
	return {"count": len(rows), "tasks": [_task_to_pwa(r) for r in rows]}


@frappe.whitelist()
def tasks_sync(tasks=None):
	"""Upsert tasks pushed from the PWA (dedupe via custom_rem_ref)."""
	if not tasks or not isinstance(tasks, list):
		frappe.throw(_("tasks must be a list"), frappe.ValidationError)
	created = updated = 0
	for item in tasks:
		if not isinstance(item, dict) or not item.get("title"):
			continue
		existing = None
		if item.get("id") and str(item["id"]).isdigit():
			existing = frappe.db.get_value("Task", {"custom_rem_ref": str(item["id"])})
		doc = frappe.get_doc("Task", existing) if existing else frappe.new_doc("Task")
		doc.flags.ignore_permissions = True
		doc.subject = str(item.get("title") or "")[:140]
		doc.custom_rem_ref = str(item.get("id") or "")
		_ts = {"To Do": "Open", "In Progress": "Working", "Done": "Completed", "Blocked": "Cancelled"}
		doc.status = _ts.get(str(item.get("status") or "To Do"), str(item.get("status") or "Open"))
		doc.custom_rem_priority = str(item.get("priority") or "Medium")
		if item.get("project"):
			# Task.project is a Link to the Project doc name — accept either the
			# doc name or the human project_name.
			_pname = str(item["project"])
			_pdoc = frappe.db.get_value("Project", {"name": _pname}, "name") or \
				frappe.db.get_value("Project", {"project_name": _pname}, "name")
			if _pdoc:
				doc.project = _pdoc
		if item.get("deadline"):
			doc.exp_start_date = str(item["deadline"])[:10]
		doc.description = str(item.get("desc") or "")
		if existing:
			doc.save()
			updated += 1
		else:
			doc.insert()
			created += 1
	frappe.db.commit()
	return {"created": created, "updated": updated}



# ═══ PLOTS & UNITS BRIDGE (PWA Plots/Blocks → ERPNext Item) ═══

PLOT_STAGES = ["available", "reserved", "sold", "not_acquired"]


def _plot_to_pwa(it):
	"""Map a native Item (with REM custom fields) to the PWA plot contract."""
	return {
		"id": it.item_code or "",
		"type": it.custom_rem_type or "3 Katha",
		"status": it.custom_rem_status or "available",
		"block": it.custom_rem_block or "",
		"katha": it.custom_rem_katha or "",
		"price": _fmt_bdt(it.custom_rem_price or 0),
		"booking_ref": it.custom_rem_booking_ref or "",
		"name": it.name,
	}


@frappe.whitelist()
def plots_pipeline():
	"""Pull all REM plot Items in the PWA contract."""
	rows = frappe.get_all(
		"Item",
		# custom-field DEFAULTS get written onto every existing Item when the
		# fields are created — block is the marker that separates real plot
		# Items (A/B/C blocks) from the seeded charge/quote Items.
		filters=[["custom_rem_block", "is", "set"]],
		fields=["name", "item_code", "custom_rem_type", "custom_rem_block", "custom_rem_status",
				"custom_rem_katha", "custom_rem_price", "custom_rem_booking_ref"],
		order_by="item_code asc",
		limit_page_length=2000,
	)
	return {"count": len(rows), "plots": [_plot_to_pwa(r) for r in rows]}


@frappe.whitelist()
def plots_sync(plots=None):
	"""Upsert plots pushed from the PWA (dedupe via item_code)."""
	if not plots or not isinstance(plots, list):
		frappe.throw(_("plots must be a list"), frappe.ValidationError)
	created = updated = 0
	for item in plots:
		if not isinstance(item, dict) or not item.get("id"):
			continue
		existing = frappe.db.get_value("Item", {"item_code": str(item["id"])})
		doc = frappe.get_doc("Item", existing) if existing else frappe.new_doc("Item")
		doc.flags.ignore_permissions = True
		doc.item_code = str(item["id"])[:140]
		doc.item_name = str(item["id"])[:140]
		doc.item_group = "All Item Groups"
		doc.stock_uom = "Nos"
		doc.is_stock_item = 0
		doc.custom_rem_type = str(item.get("type") or "3 Katha")
		doc.custom_rem_block = str(item.get("block") or "")
		st = str(item.get("status") or "available")
		doc.custom_rem_status = st if st in PLOT_STAGES else "available"
		doc.custom_rem_katha = str(item.get("katha") or "")
		doc.custom_rem_price = parse_bdt(item.get("price"))
		doc.custom_rem_booking_ref = str(item.get("booking_ref") or "")
		if existing:
			doc.save()
			updated += 1
		else:
			doc.insert()
			created += 1
	frappe.db.commit()
	return {"created": created, "updated": updated}


@frappe.whitelist()
def plot_update_status(name=None, status=None, booking_ref=None):
	"""Set a plot's status (available/reserved/sold/not_acquired)."""
	if not name or status not in PLOT_STAGES:
		frappe.throw(_("Invalid plot/status"), frappe.ValidationError)
	doc = frappe.get_doc("Item", name)
	doc.custom_rem_status = status
	if booking_ref is not None:
		doc.custom_rem_booking_ref = str(booking_ref)
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return _plot_to_pwa(doc)



# ═══ FINANCE BRIDGE (PWA Finance → native ERPNext accounting) ═══

ROOT_TYPE_MAP = {"Asset": "Asset", "Liability": "Liability", "Income": "Income", "Expense": "Expense"}


def _gl_balance(account):
	"""Live GL balance for an account (debit - credit)."""
	row = frappe.db.sql(
		"SELECT SUM(debit) - SUM(credit) FROM `tabGL Entry` WHERE account=%s AND is_cancelled=0",
		account,
	)
	return float(row[0][0] or 0) if row else 0.0


def _acc_to_pwa(a, bal):
	return {
		"code": a.name,
		"name": a.account_name or a.name,
		"type": ROOT_TYPE_MAP.get(a.root_type or a.report_type or "", a.root_type or "Asset"),
		"balance": _fmt_bdt(bal),
	}


@frappe.whitelist()
def finance_pipeline():
	"""Pull the real chart of accounts (with live GL balances), bank accounts, journals."""
	# 1. Chart of accounts — non-group accounts with live balances
	accts = frappe.get_all(
		"Account",
		filters={"is_group": 0, "disabled": 0},
		fields=["name", "account_name", "root_type", "report_type"],
		order_by="name asc",
		limit_page_length=2000,
	)
	coa = []
	for a in accts:
		bal = _gl_balance(a.name)
		# only include accounts that have activity or are in the PWA's set
		coa.append(_acc_to_pwa(a, bal))

	# 2. Bank accounts (native Bank Account doctype)
	banks = frappe.get_all(
		"Bank Account",
		fields=["name", "bank", "account_name", "account", "account_type"],
		order_by="name asc",
		limit_page_length=200,
	)
	bank_list = []
	for b in banks:
		bank_list.append({
			"name": b.bank or b.name or "",
			"account": b.account or b.account_name or "",
			"branch": "",
			"type": b.account_type or "",
			"balance": "৳0",
		})

	# 3. Journal entries (native)
	journals = frappe.get_all(
		"Journal Entry",
		filters={"docstatus": 1},
		fields=["name", "posting_date", "user_remark", "total_debit", "voucher_type"],
		order_by="posting_date desc",
		limit_page_length=200,
	)
	journal_list = []
	for j in journals:
		journal_list.append({
			"id": j.name,
			"date": str(j.posting_date or "")[:10],
			"ref": j.voucher_type or "",
			"desc": (j.user_remark or "")[:120],
			"total": j.total_debit or 0,
		})

	return {
		"coa": coa,
		"banks": bank_list,
		"journals": journal_list,
		"counts": {"coa": len(coa), "banks": len(bank_list), "journals": len(journal_list)},
	}


def _resolve_account(acc_ref):
	"""Resolve a PWA account ref ('1-1000 Cash & Bank' or '1110 - Cash - MC') to a native Account name."""
	if not acc_ref:
		return ""
	# 1. exact match
	if frappe.db.exists("Account", acc_ref):
		return acc_ref
	# 2. match by account_name (case-insensitive)
	name_part = acc_ref.split(" ", 1)[-1].strip() if " " in acc_ref else acc_ref
	row = frappe.db.sql(
		"SELECT name FROM `tabAccount` WHERE is_group=0 AND LOWER(account_name)=LOWER(%s) LIMIT 1",
		name_part,
	)
	if row:
		return row[0][0]
	# 3. fuzzy: account_name LIKE %part%
	row = frappe.db.sql(
		"SELECT name FROM `tabAccount` WHERE is_group=0 AND LOWER(account_name) LIKE LOWER(%s) LIMIT 1",
		"%" + name_part + "%",
	)
	if row:
		return row[0][0]
	return ""


@frappe.whitelist()
def journal_sync(journals=None):
	"""Create native Journal Entries from PWA journals (one per journal)."""
	if not journals or not isinstance(journals, list):
		frappe.throw(_("journals must be a list"), frappe.ValidationError)
	created = skipped = 0
	company = frappe.db.get_single_value("Global Defaults", "default_company") or ""
	for item in journals:
		if not isinstance(item, dict) or not item.get("lines") or not item["lines"]:
			continue
		# skip if already synced (dedupe via custom_rem_ref — JE title is auto-set)
		if item.get("id") and frappe.db.get_value("Journal Entry", {"custom_rem_ref": str(item["id"])}):
			skipped += 1
			continue
		entries = []
		valid = True
		for ln in item["lines"] or []:
			acc = _resolve_account(ln.get("acc") or "")
			if not acc:
				valid = False
				break
			line = {
				"account": acc,
				"debit_in_account_currency": float(ln.get("dr") or 0),
				"credit_in_account_currency": float(ln.get("cr") or 0),
			}
			# AR/AP accounts need party_type + party on the line
			at = frappe.db.get_value("Account", acc, "account_type")
			if at in ("Receivable", "Payable"):
				if not ln.get("party_type") or not ln.get("party"):
					valid = False
					break
				line["party_type"] = str(ln["party_type"])
				line["party"] = str(ln["party"])
			entries.append(line)
		if not valid:
			skipped += 1
			continue
		je = frappe.get_doc({
			"doctype": "Journal Entry",
			"posting_date": str(item.get("date") or "")[:10] or frappe.utils.today(),
			"user_remark": "REM-" + str(item.get("id") or "") + " " + str(item.get("desc") or "")[:100],
			"custom_rem_ref": str(item.get("id") or ""),
			"company": company,
			"voucher_type": "Journal Entry",
			"accounts": entries,
		})
		je.flags.ignore_permissions = True
		je.flags.ignore_mandatory = True
		frappe.set_user("Administrator")
		try:
			je.insert()
			je.submit()
			created += 1
		except Exception:
			frappe.db.rollback()
			skipped += 1
		finally:
			frappe.set_user(frappe.session.user)
	frappe.db.commit()
	return {"created": created, "skipped": skipped}



# ═══ INVOICES & PAYMENTS BRIDGE (real Sales Invoice / Payment Entry → PWA) ═══

@frappe.whitelist()
def invoices_pipeline():
	"""Pull submitted Sales Invoices in the PWA invoice contract."""
	rows = frappe.get_all(
		"Sales Invoice",
		filters={"docstatus": 1},
		fields=["name", "customer_name", "posting_date", "due_date", "grand_total", "status", "outstanding_amount"],
		order_by="posting_date desc",
		limit_page_length=300,
	)
	out = []
	for r in rows:
		out.append({
			"id": r.name,
			"client": r.customer_name or "",
			"project": "",
			"unit": "",
			"amount": r.grand_total or 0,
			"status": _inv_status(r.status, r.outstanding_amount),
			"dueDate": str(r.due_date or "")[:10],
			"issuedDate": str(r.posting_date or "")[:10],
			"desc": "",
			"items": [],
		})
	return {"count": len(out), "invoices": out}


def _inv_status(erp_status, outstanding):
	"""Map ERPNext Sales Invoice status → PWA status."""
	erp_status = erp_status or ""
	if "Paid" in erp_status:
		return "Paid"
	if "Overdue" in erp_status:
		return "Overdue"
	if float(outstanding or 0) > 0:
		return "Unpaid"
	return erp_status or "Paid"


@frappe.whitelist()
def payments_pipeline():
	"""Pull submitted Payment Entries in the PWA payment contract."""
	rows = frappe.get_all(
		"Payment Entry",
		filters={"docstatus": 1, "payment_type": "Receive"},
		fields=["name", "party", "posting_date", "paid_amount", "mode_of_payment", "reference_no"],
		order_by="posting_date desc",
		limit_page_length=300,
	)
	out = []
	for r in rows:
		out.append({
			"id": r.name,
			"invoiceId": "",
			"client": r.party or "",
			"amount": r.paid_amount or 0,
			"date": str(r.posting_date or "")[:10],
			"method": r.mode_of_payment or "",
			"reference": r.reference_no or "",
			"status": "Cleared",
			"notes": "",
		})
	return {"count": len(out), "payments": out}



# ═══ CONSTRUCTION BRIDGE (contractors/work orders/equipment → ERPNext) ═══

WO_STAGES = ["Pending Review", "Approved", "In Progress", "Completed", "Overdue", "Cancelled"]


@frappe.whitelist()
def contractors_pipeline():
	"""Pull REM contractor Suppliers in the PWA contract."""
	rows = frappe.get_all(
		"Supplier",
		filters=[["custom_rem_type", "is", "set"]],
		fields=["name", "supplier_name", "custom_rem_type", "custom_rem_rating", "custom_rem_license",
				"custom_rem_insurance", "custom_rem_status", "mobile_no", "email_id"],
		order_by="name asc",
		limit_page_length=500,
	)
	out = []
	for s in rows:
		out.append({
			"id": s.name,
			"name": s.supplier_name or s.name,
			"type": s.custom_rem_type or "",
			"contact": s.mobile_no or "",
			"email": s.email_id or "",
			"rating": s.custom_rem_rating or 0,
			"status": s.custom_rem_status or "Active",
			"license": s.custom_rem_license or "",
			"insurance": s.custom_rem_insurance or "",
			"projects": [],
		})
	return {"count": len(out), "contractors": out}


@frappe.whitelist()
def contractors_sync(contractors=None):
	"""Upsert contractors pushed from the PWA (dedupe via Supplier name)."""
	if not contractors or not isinstance(contractors, list):
		frappe.throw(_("contractors must be a list"), frappe.ValidationError)
	created = updated = 0
	for item in contractors:
		if not isinstance(item, dict) or not item.get("name"):
			continue
		existing = frappe.db.get_value("Supplier", {"supplier_name": str(item["name"])})
		doc = frappe.get_doc("Supplier", existing) if existing else frappe.new_doc("Supplier")
		doc.flags.ignore_permissions = True
		doc.supplier_name = str(item["name"])[:140]
		doc.supplier_group = frappe.db.get_value("Supplier Group", {"is_group": 0}, "name") or "All Supplier Groups"
		doc.custom_rem_type = str(item.get("type") or "Civil Works")
		doc.custom_rem_rating = int(item.get("rating") or 0)
		doc.custom_rem_license = str(item.get("license") or "")
		doc.custom_rem_insurance = str(item.get("insurance") or "")
		st = str(item.get("status") or "Active")
		doc.custom_rem_status = st if st in ("Active", "Inactive") else "Active"
		doc.mobile_no = str(item.get("contact") or "")
		doc.email_id = str(item.get("email") or "")
		if existing:
			doc.save()
			updated += 1
		else:
			doc.insert()
			created += 1
	frappe.db.commit()
	return {"created": created, "updated": updated}


@frappe.whitelist()
def work_orders_pipeline():
	"""Pull REM Work Orders in the PWA contract."""
	rows = frappe.get_all(
		"REM Work Order",
		fields=["name", "wo_ref", "contractor_name", "project", "scope", "amount", "date", "deadline", "status"],
		order_by="creation desc",
		limit_page_length=500,
	)
	out = []
	for w in rows:
		out.append({
			"id": w.wo_ref or w.name,
			"contractor": w.contractor_name or "",
			"project": w.project or "",
			"scope": w.scope or "",
			"amount": w.amount or 0,
			"date": str(w.date or "")[:10],
			"deadline": str(w.deadline or "")[:10],
			"status": w.status or "Pending Review",
			"name": w.name,
		})
	return {"count": len(out), "workOrders": out}


@frappe.whitelist()
def work_orders_sync(workOrders=None):
	"""Upsert work orders pushed from the PWA (dedupe via wo_ref)."""
	if not workOrders or not isinstance(workOrders, list):
		frappe.throw(_("workOrders must be a list"), frappe.ValidationError)
	created = updated = 0
	for item in workOrders:
		if not isinstance(item, dict) or not item.get("scope"):
			continue
		existing = None
		if item.get("id"):
			existing = frappe.db.get_value("REM Work Order", {"wo_ref": str(item["id"])})
		doc = frappe.get_doc("REM Work Order", existing) if existing else frappe.new_doc("REM Work Order")
		doc.flags.ignore_permissions = True
		doc.wo_ref = str(item.get("id") or "")[:40]
		doc.contractor_name = str(item.get("contractor") or "")[:140]
		doc.project = str(item.get("project") or "")[:140]
		doc.scope = str(item.get("scope") or "")[:400]
		doc.amount = parse_bdt(item.get("amount")) if isinstance(item.get("amount"), str) else (item.get("amount") or 0)
		if item.get("date"):
			doc.date = str(item["date"])[:10]
		if item.get("deadline"):
			doc.deadline = str(item["deadline"])[:10]
		st = str(item.get("status") or "Pending Review")
		doc.status = st if st in WO_STAGES else "Pending Review"
		if existing:
			doc.save()
			updated += 1
		else:
			doc.insert()
			created += 1
	frappe.db.commit()
	return {"created": created, "updated": updated}


@frappe.whitelist()
def equipment_pipeline():
	"""Pull REM equipment Assets in the PWA contract."""
	rows = frappe.get_all(
		"Asset",
		filters=[["custom_rem_ref", "is", "set"]],
		fields=["name", "asset_name", "custom_rem_ref", "custom_rem_model", "custom_rem_type", "custom_rem_site",
				"custom_rem_status", "custom_rem_hours", "custom_rem_fuel_cost", "custom_rem_operator",
				"custom_rem_last_service"],
		order_by="name asc",
		limit_page_length=500,
	)
	out = []
	for e in rows:
		out.append({
			"id": e.custom_rem_ref or e.name,
			"name": e.asset_name or e.name,
			"model": e.custom_rem_model or "",
			"type": e.custom_rem_type or "Heavy",
			"site": e.custom_rem_site or "",
			"status": e.custom_rem_status or "Operational",
			"hours": e.custom_rem_hours or "",
			"fuelCost": e.custom_rem_fuel_cost or 0,
			"operator": e.custom_rem_operator or "",
			"lastService": str(e.custom_rem_last_service or "")[:10],
		})
	return {"count": len(out), "equipment": out}


@frappe.whitelist()
def equipment_sync(equipment=None):
	"""Upsert equipment pushed from the PWA (dedupe via custom_rem_ref)."""
	if not equipment or not isinstance(equipment, list):
		frappe.throw(_("equipment must be a list"), frappe.ValidationError)
	created = updated = 0
	for item in equipment:
		if not isinstance(item, dict) or not item.get("name"):
			continue
		existing = None
		if item.get("id"):
			existing = frappe.db.get_value("Asset", {"custom_rem_ref": str(item["id"])})
		doc = frappe.get_doc("Asset", existing) if existing else frappe.new_doc("Asset")
		doc.flags.ignore_permissions = True
		doc.asset_name = str(item.get("name") or "")[:140]
		doc.custom_rem_ref = str(item.get("id") or "")
		doc.custom_rem_model = str(item.get("model") or "")
		doc.custom_rem_type = str(item.get("type") or "Heavy")
		doc.custom_rem_site = str(item.get("site") or "")
		st = str(item.get("status") or "Operational")
		doc.custom_rem_status = st if st in ("Operational", "Under Repair", "Idle", "Maintenance") else "Operational"
		doc.custom_rem_hours = str(item.get("hours") or "")
		doc.custom_rem_fuel_cost = parse_bdt(item.get("fuelCost")) if isinstance(item.get("fuelCost"), str) else (item.get("fuelCost") or 0)
		doc.custom_rem_operator = str(item.get("operator") or "")
		if item.get("lastService"):
			doc.custom_rem_last_service = str(item["lastService"])[:10]
		# Asset requires the linked Item to be a Fixed Asset item
		_itm = _get_sales_item()
		frappe.db.set_value("Item", _itm, "is_fixed_asset", 1)
		doc.item_code = _itm
		# Asset has mandatory gross_purchase_amount + purchase_date
		doc.gross_purchase_amount = doc.custom_rem_fuel_cost or 0
		doc.purchase_date = frappe.utils.today()
		loc = frappe.db.get_value("Location", {}, "name")
		if not loc:
			ld = frappe.new_doc("Location")
			ld.flags.ignore_permissions = True
			ld.location_name = "REM Main Site"
			ld.insert()
			loc = ld.name
		doc.location = loc
		if existing:
			doc.save()
			updated += 1
		else:
			doc.insert()
			created += 1
	frappe.db.commit()
	return {"created": created, "updated": updated}


# ═══ REM SETTINGS (PWA v2.0 server-backed connection config) ═══

def _rem_settings():
	"""REM Settings single as a plain dict (never raises)."""
	try:
		doc = _rem_settings_doc()
		return {
			"pwa_version": doc.pwa_version or "2.0.0",
			"api_base_override": doc.api_base_override or "",
			"auto_connect": bool(doc.auto_connect),
			"push_on_save": bool(doc.push_on_save),
			"auto_heal": bool(doc.auto_heal),
			"live_land": bool(doc.live_land),
			"session_expiry": doc.session_expiry_hint or "",
			"last_connected_user": doc.last_connected_user or "",
			"last_sync_time": doc.last_sync_time or "",
		}
	except Exception:
		return {
			"pwa_version": "2.0.0",
			"api_base_override": "",
			"auto_connect": True,
			"push_on_save": True,
			"auto_heal": True,
			"live_land": True,
			"session_expiry": "",
			"last_connected_user": "",
			"last_sync_time": "",
		}


def _rem_settings_doc():
	"""Get-or-create the REM Settings single document.

	NOTE: frappe.db.exists() on a Single doctype name matches the DocType row
	in tabDocType, NOT the singles record — always get-or-create via try/except.
	"""
	try:
		return frappe.get_doc("REM Settings", "REM Settings")
	except frappe.DoesNotExistError:
		# Create via db_set (no permission checks, no sbool coercion).
		doc = frappe.new_doc("REM Settings")
		doc.pwa_version = "2.0.0"
		doc.auto_connect = 1
		doc.push_on_save = 1
		doc.auto_heal = 1
		doc.live_land = 1
		doc.flags.ignore_permissions = True
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		return frappe.get_doc("REM Settings", "REM Settings")


def _session_expiry_hint():
	"""Mirror ERPNext System Settings session_expiry (e.g. '06:00:00')."""
	try:
		return frappe.db.get_single_value("System Settings", "session_expiry") or ""
	except Exception:
		return ""


@frappe.whitelist()
def settings_get():
	"""Return the server-backed connection config (REM Settings)."""
	return _rem_settings()


@frappe.whitelist()
def settings_set(settings=None):
	"""Persist PWA connection config into REM Settings (server-side, shared)."""
	if not settings or not isinstance(settings, dict):
		frappe.throw(_("settings must be an object"), frappe.ValidationError)
	allowed = {
		"pwa_version", "api_base_override", "auto_connect", "push_on_save",
		"auto_heal", "live_land",
	}
	doc = _rem_settings_doc()  # ensure the single exists
	for k, v in settings.items():
		if k not in allowed:
			continue
		# db_set() bypasses doctype permissions (the whitelisted endpoint is the
		# guard) and does NOT sbool-coerce — set_single_value() turns "2.0.0"
		# into 1 via sbool, corrupting Data fields.
		if k in ("auto_connect", "push_on_save", "auto_heal", "live_land"):
			doc.db_set(k, 1 if v else 0)
		else:
			doc.db_set(k, str(v or ""))
	# keep the session-expiry hint current from System Settings
	doc.db_set("session_expiry_hint", _session_expiry_hint())
	frappe.db.commit()
	return _rem_settings()


@frappe.whitelist(allow_guest=True)
def index():
    """GET-able landing for the API base URL: endpoint map + health."""
    endpoints = [
        "index",
        "login",
        "logout",
        "bootstrap",
        "sync",
        "land_pipeline",
        "land_sync",
        "land_legal_checklist",
        "land_legal_update",
        "land_legal_load_standard",
        "download_invoice",
        "demo_confirm",
        "settings_get",
        "settings_set",
        "leads_pipeline",
        "leads_sync",
        "lead_update_status",
        "bookings_pipeline",
        "bookings_sync",
        "booking_update_status",
        "booking_invoice",
        "booking_payment",
        "projects_pipeline",
        "projects_sync",
        "tasks_pipeline",
        "tasks_sync",
        "plots_pipeline",
        "plots_sync",
        "plot_update_status",
        "finance_pipeline",
        "journal_sync",
        "invoices_pipeline",
        "payments_pipeline",
        "contractors_pipeline",
        "contractors_sync",
        "work_orders_pipeline",
        "work_orders_sync",
        "equipment_pipeline",
        "equipment_sync",
    ]
    return {
        "service": "MARS Constech REM ERP API bridge",
        "status": "ok",
        "usage": "Append an endpoint to this base URL, e.g. .../api.method.login",
        "endpoints": endpoints,
        "server_time": frappe.utils.now(),
    }
