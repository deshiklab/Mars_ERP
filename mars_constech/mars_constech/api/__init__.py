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
	return {
		"token": token,
		"full_name": frappe.utils.get_fullname(user),
		"user": user,
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
		"meta": {"server_time": frappe.utils.now(), "source": "frappe"},
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
    ]
    return {
        "service": "MARS Constech REM ERP API bridge",
        "status": "ok",
        "usage": "Append an endpoint to this base URL, e.g. .../api.method.login",
        "endpoints": endpoints,
        "server_time": frappe.utils.now(),
    }
