frappe.pages["rem-executive-dashboard"].on_page_load = function (wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: "REM Executive Dashboard",
        single_column: true,
    });

    let $body = $(wrapper).find(".page-content");
    $body.html(`
        <div id="rem-exec-root" style="padding:12px">
            <div style="display:flex;gap:8px;margin-bottom:14px;align-items:center">
                <button class="btn btn-primary btn-sm" onclick="frappe.pages['rem-executive-dashboard'].refresh()">
                    ⟳ Refresh
                </button>
                <span class="text-muted" style="font-size:12px">Live counts from the mars_constech bridge doctypes · auto-refreshes every 60s</span>
            </div>
            <div id="rem-exec-body"><div class="text-muted">Loading…</div></div>
        </div>
    `);

    wrapper.page.rem_exec_timer = setInterval(function () {
        frappe.pages["rem-executive-dashboard"].refresh(true);
    }, 60000);

    this.refresh = function (silent) {
        if (!silent) frappe.pages["rem-executive-dashboard"].refresh(true);
    };
};

frappe.pages["rem-executive-dashboard"].refresh = function () {
    let $body = $("#rem-exec-body");
    frappe.call({
        method: "mars_constech.mars_constech.page.rem_executive_dashboard.rem_executive_dashboard.get_exec_summary",
        callback: function (r) {
            if (!r.message) return;
            const d = r.message;
            const fmt = (v) => "৳ " + Number(v || 0).toLocaleString("en-IN");
            const cards = [
                ["Sales & CRM", [
                    ["Leads", d.leads], ["Bookings", d.bookings],
                    ["Booking value", fmt(d.booking_value)], ["Customers", d.customers],
                ]],
                ["Land & Legal", [
                    ["Acquisitions", d.land_acquisitions],
                    ["Legal pending", d.land_pending_legal, d.land_pending_legal > 0 ? "danger" : "success"],
                ]],
                ["Dues & Finance", [
                    ["Dues outstanding", fmt(d.dues_outstanding), d.dues_outstanding > 0 ? "warning" : "success"],
                    ["Invoice outstanding", fmt(d.invoices_outstanding), d.invoices_outstanding > 0 ? "warning" : "success"],
                    ["Invoices paid", d.invoices_paid],
                ]],
                ["HR", [
                    ["Active employees", d.employees], ["Attendance today", d.attendance_today],
                    ["Leave pending", d.leave_pending, d.leave_pending > 0 ? "warning" : "success"],
                    ["Labor on site", d.labor],
                ]],
                ["Stock & Procurement", [
                    ["Stock items", d.stock_items],
                    ["Low stock", d.low_stock, d.low_stock > 0 ? "danger" : "success"],
                    ["Open POs", d.pos_open],
                ]],
                ["Construction & Post-Sales", [
                    ["Projects", d.projects], ["Work orders", d.work_orders],
                    ["Handovers pending", d.handovers_pending, d.handovers_pending > 0 ? "warning" : "success"],
                    ["Approvals pending", d.approvals_pending, d.approvals_pending > 0 ? "warning" : "success"],
                ]],
                ["Assets & Support", [
                    ["Assets in use", d.assets], ["Open tickets", d.tickets_open],
                ]],
            ];
            let html = '<div class="row">';
            cards.forEach(function (group) {
                html += `<div class="col-sm-6 col-md-4" style="margin-bottom:10px">
                    <div class="panel panel-default" style="border:1px solid #eee;border-radius:8px;margin-bottom:0">
                        <div class="panel-heading" style="background:#f8f9fa;padding:8px 12px;font-weight:600;font-size:13px;border-bottom:1px solid #eee;border-radius:8px 8px 0 0">${group[0]}</div>
                        <div class="panel-body" style="padding:10px 12px">`;
                group[1].forEach(function (c) {
                    const cls = c[2] === "danger" ? "#c62828" : c[2] === "warning" ? "#e65100" : "#222";
                    html += `<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px dashed #f0f0f0;font-size:13px">
                        <span class="text-muted">${c[0]}</span>
                        <span style="font-weight:600;color:${cls}">${c[1]}</span>
                    </div>`;
                });
                html += `</div></div></div>`;
            });
            html += '</div><div class="text-muted" style="font-size:11px;margin-top:6px">MARS Constech · REM ERP · updated ' + new Date().toLocaleTimeString() + '</div>';
            $body.html(html);
        },
    });
};

$(document).on("page-change", function () {
    if (cur_page && cur_page.page_name === "rem-executive-dashboard") {
        frappe.pages["rem-executive-dashboard"].refresh(true);
    }
});
