// Copyright (c) 2019, youssef restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Administrative Communications', {
	validate: function(frm) {
		frm.set_df_property("section_break_18", "hidden", 0);
		if (cur_frm.doc.owner_user != cur_frm.selected_doc["owner"]){
			frm.set_value("owner_user",cur_frm.selected_doc["owner"]);
		};

		if (cur_frm.doc.edited_user != frappe.user.name){
			frm.set_value("edited_user",frappe.user.name);	
		};

	},

	refresh: function(frm) {
		if (cur_frm.doc.owner_user == frappe.user.name){
			frm.set_df_property("status", "read_only", 0);
		};
		
	},

	onload: function(frm) {
		if (frm.is_new()) {
			frm.set_df_property("section_break_18", "hidden", 1);
		};
	},
	
});