frappe.ui.form.on("Land Acquisition", {
	refresh: function (frm) {
		// Legal team action: load the standard checklist (only when empty)
		if (frm.doc.current_stage === "Due Diligence" && (!frm.doc.legal_checklist || frm.doc.legal_checklist.length === 0)) {
			frm.add_custom_button(__("Load Standard Legal Checklist"), function () {
				frappe.call({
					method: "load_checklist_from_form",
					doc: frm.doc,
					callback: function (r) {
						if (r.message && r.message.count) {
							frappe.msgprint(__("Loaded {0} checklist items. The legal team must now collect and vet each document.", [r.message.count]));
							frm.reload_doc();
						}
					},
				});
			});
		}
	},
});
