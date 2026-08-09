frappe.pages["rem-settings-manager"].on_page_load = function (wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: "REM Settings Manager",
        single_column: true,
    });

    let $body = $(wrapper).find(".page-content");
    $body.html(`
        <div id="rem-settings-root" style="padding:12px;max-width:720px">
            <div class="alert alert-info" style="font-size:12px">
                These are the <b>server-backed</b> PWA connection settings (REM Settings Single doctype).
                Every browser/device that connects to this ERPNext picks them up — changes here propagate
                to all PWA clients. The PWA also writes here from its Settings → Server Sync screen.
            </div>
            <div id="rem-settings-form" class="panel panel-default" style="border:1px solid #eee;border-radius:8px">
                <div class="panel-body" style="padding:16px">
                    <div class="form-group">
                        <label>PWA version (server ships this)</label>
                        <input class="form-control" id="rs_pwa_version" placeholder="2.3.0">
                    </div>
                    <div class="form-group">
                        <label>API base override (empty = auto-derive from origin)</label>
                        <input class="form-control" id="rs_api_override" placeholder="http://localhost:8000/api/method/mars_constech.mars_constech.api">
                    </div>
                    <div class="checkbox"><label><input type="checkbox" id="rs_auto_connect"> Auto-connect on load</label></div>
                    <div class="checkbox"><label><input type="checkbox" id="rs_push_on_save"> Push on every save (debounced)</label></div>
                    <div class="checkbox"><label><input type="checkbox" id="rs_auto_heal"> Auto-heal stale URL</label></div>
                    <div class="checkbox"><label><input type="checkbox" id="rs_live_land"> Live land pipeline (Legal Vetting reads ERP)</label></div>
                    <div style="margin-top:12px;display:flex;gap:8px">
                        <button class="btn btn-primary btn-sm" onclick="frappe.pages['rem-settings-manager'].save()">💾 Save to ERPNext</button>
                        <button class="btn btn-default btn-sm" onclick="frappe.pages['rem-settings-manager'].load()">⟳ Reload</button>
                    </div>
                </div>
            </div>
            <div id="rem-settings-sys" class="panel panel-default" style="border:1px solid #eee;border-radius:8px;margin-top:12px">
                <div class="panel-heading" style="background:#f8f9fa;padding:8px 12px;font-weight:600;font-size:13px;border-bottom:1px solid #eee">System info (read-only)</div>
                <div class="panel-body" style="padding:12px;font-size:13px" id="rem-settings-sys-body">Loading…</div>
            </div>
        </div>
    `);

    this.load = function () {
        frappe.call({
            method: "mars_constech.mars_constech.page.rem_settings_manager.rem_settings_manager.get_settings",
            callback: function (r) {
                if (!r.message) return;
                const s = r.message;
                $("#rs_pwa_version").val(s.pwa_version);
                $("#rs_api_override").val(s.api_base_override);
                $("#rs_auto_connect").prop("checked", s.auto_connect);
                $("#rs_push_on_save").prop("checked", s.push_on_save);
                $("#rs_auto_heal").prop("checked", s.auto_heal);
                $("#rs_live_land").prop("checked", s.live_land);
                $("#rem-settings-sys-body").html(
                    "<div><b>Session expiry (System Settings):</b> " + (s.session_expiry_hint || "—") + "</div>" +
                    "<div><b>Last connected user:</b> " + (s.last_connected_user || "—") + "</div>" +
                    "<div><b>Last sync:</b> " + (s.last_sync_time || "—") + "</div>"
                );
            },
        });
    };

    this.save = function () {
        const settings = {
            pwa_version: $("#rs_pwa_version").val(),
            api_base_override: $("#rs_api_override").val(),
            auto_connect: $("#rs_auto_connect").is(":checked") ? 1 : 0,
            push_on_save: $("#rs_push_on_save").is(":checked") ? 1 : 0,
            auto_heal: $("#rs_auto_heal").is(":checked") ? 1 : 0,
            live_land: $("#rs_live_land").is(":checked") ? 1 : 0,
        };
        frappe.call({
            method: "mars_constech.mars_constech.page.rem_settings_manager.rem_settings_manager.save_settings",
            args: { settings: settings },
            callback: function (r) {
                if (r.message && r.message.ok) {
                    frappe.show_alert({ message: "REM Settings saved to ERPNext — PWA clients pick it up on next sync", indicator: "green" });
                    frappe.pages["rem-settings-manager"].load();
                } else {
                    frappe.show_alert({ message: "Save failed: " + JSON.stringify(r.exc || r.message), indicator: "red" });
                }
            },
        });
    };

    this.load();
};
