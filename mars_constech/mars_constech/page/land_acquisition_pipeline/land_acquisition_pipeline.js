frappe.pages["land-acquisition-pipeline"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: "Land Acquisition Pipeline",
		single_column: true,
	});

	const page = wrapper.page;
	page.add_inner_button("+ New Acquisition", () => {
		frappe.new_doc("Land Acquisition");
	});
	page.add_inner_button("Refresh", () => load_pipeline());

	let $body = $(wrapper).find(".page-content");

	// stage color map (mirrors V10)
	const COLORS = {
		Lead: "#3b82f6",
		Survey: "#06b6d4",
		Negotiation: "#f97316",
		Agreement: "#8b5cf6",
		Registration: "#eab308",
		Handover: "#22c55e",
	};

	function load_pipeline() {
		$body.html(`<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-2 text-muted">Loading pipeline…</p></div>`);
		frappe.call({
			method: "mars_constech.mars_constech.page.land_acquisition_pipeline.land_acquisition_pipeline.get_pipeline",
			callback: (r) => {
				if (r.message) render(r.message);
				else $body.html(`<div class="alert alert-warning">Failed to load pipeline</div>`);
			},
			error: () => $body.html(`<div class="alert alert-danger">Failed to load pipeline</div>`),
		});
	}

	function fmtCr(v) {
		if (!v) return "—";
		return `৳${(v / 10000000).toFixed(1)} Cr`;
	}

	function render(data) {
		const $board = $(
			`<div style="display:flex;gap:12px;overflow-x:auto;padding:16px 8px;align-items:flex-start;">
				${data.stages.map((s) => `
					<div class="kanban-col" data-stage="${s}" style="flex:0 0 290px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;min-height:200px;">
						<div class="kanban-head" style="display:flex;align-items:center;gap:8px;padding:12px 14px;border-bottom:2px solid ${COLORS[s]};">
							<span style="width:10px;height:10px;border-radius:50%;background:${COLORS[s]};"></span>
							<strong style="flex:1;color:#1e293b;">${s}</strong>
							<span class="badge badge-light">${data.groups[s].length}</span>
						</div>
						<div class="kanban-cards" style="padding:10px;">
							${data.groups[s].map(card).join("") || `<div class="text-muted text-center py-3" style="font-size:12px;">No records</div>`}
						</div>
					</div>`).join("")}
				</div>`);
		$body.html($board);

		// simple drag-free stage jump: click chevron to move forward
		$board.find(".js-advance").on("click", function () {
			const name = $(this).data("name");
			const stage = $(this).data("stage");
			const stages = data.stages;
			const idx = stages.indexOf(stage);
			if (idx < stages.length - 1) {
				frappe.call({
					method: "frappe.client.set_value",
					args: {
						doctype: "Land Acquisition",
						name: name,
						fieldname: "current_stage",
						value: stages[idx + 1],
					},
					callback: () => load_pipeline(),
				});
			}
		});
	}

	function card(r) {
		return `
			<div class="kanban-card" data-name="${r.name}" style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:10px;cursor:pointer;box-shadow:0 1px 2px rgba(0,0,0,.05);" onclick="frappe.set_route('Form', 'Land Acquisition', '${r.name}')">
				<div style="font-weight:600;font-size:13px;color:#0f172a;">${r.land_acquisition_title || r.name}</div>
				<div style="font-size:12px;color:#64748b;margin-top:4px;">${r.land_location || ""} ${r.area_katha ? "· " + r.area_katha + " katha" : ""}</div>
				<div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;">
					<div>
						<div style="font-size:12px;color:#475569;">${fmtCr(r.deal_value || r.negotiated_price)}</div>
						<div style="font-size:11px;color:#94a3b8;">Score: ${r.feasibility_score || 0}%</div>
					</div>
					<div style="display:flex;gap:6px;align-items:center;">
						${r.legal_status === "Cleared" ? `<span class="badge badge-success" style="font-size:10px;">Legal ✓</span>` : ""}
						${data.stages.indexOf(r.current_stage) < data.stages.length - 1 ? `<button class="btn btn-xs btn-light js-advance" data-name="${r.name}" data-stage="${r.current_stage}" title="Move to next stage" style="padding:2px 8px;font-size:12px;">→</button>` : ""}
					</div>
				</div>
			</div>`;
	}

	load_pipeline();
};
