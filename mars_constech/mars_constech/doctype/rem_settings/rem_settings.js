frappe.ui.form.on('REM Settings', {
	refresh: function(frm) {
		frm.add_custom_button(__('Reset to Defaults'), function() {
			frm.set_value('auto_connect', 1);
			frm.set_value('push_on_save', 1);
			frm.set_value('auto_heal', 1);
			frm.set_value('live_land', 1);
			frm.set_value('api_base_override', '');
			frm.save();
		});
	}
});
