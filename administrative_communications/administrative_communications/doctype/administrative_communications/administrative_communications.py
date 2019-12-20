# -*- coding: utf-8 -*-
# Copyright (c) 2019, youssef restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe.utils
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address, today, format_datetime, now, nowdate, getdate, split_emails
from frappe.core.doctype.communication.email import make
from frappe.core.doctype.communication import email
from frappe.desk.form.utils import add_comment



class AdministrativeCommunications(Document):
	def validate(self):
		self.add_log()
		self.set_indicator()
		self.update_due_date()
		self.put_last_message()
		self.put_messeges()
		self.add_shaerd_with()
		self.assign_to_user()
		self.add_recipients()
		self.add_transaction_comment()
		self.set_indicator()
		self.clear_transaction_fileds()
		# self.set_overdue()




	def add_log(self):
		if not self.is_new():
			if self.transaction_type or self.transaction_detailed or self.notes :
				new_log_row = self.append('ac_log', {})
				new_log_row.transaction_type = self.transaction_type
				new_log_row.transaction_detailed = self.transaction_detailed
				new_log_row.transaction_due_date = self.transaction_due_date
				new_log_row.transaction_from = self.edited_user
				new_log_row.transaction_from_name = self.edited_user_name
				new_log_row.transaction_to = self.transaction_to
				new_log_row.transaction_to_name = self.transaction_to_name
				new_log_row.transaction_notes = self.notes
				new_log_row.attached_file = self.attached_file
				new_log_row.transaction_date = nowdate()
				new_log_row.transaction_time = now()
				frappe.db.commit()
				frappe.msgprint(_("Added Transaction Log : ") + str(self.notes))

	
	def clear_transaction_fileds(self):
		self.transaction_type = None
		self.transaction_detailed = None
		self.transaction_due_date = None
		self.transaction_to = None
		self.transaction_to_name = None
		self.attached_file = None
		self.notes = None
		self.tag = None
		self.assign_to = None
		frappe.db.commit()

	def update_due_date(self):
		if self.transaction_due_date:
			self.due_date = self.transaction_due_date

	
	def add_shaerd_with(self):
		from frappe.share import add
		if self.transaction_to:
			add(
				doctype = 'Administrative Communications', 
				name = self.name, 
				user = self.transaction_to, 
				read = 1, 
				write = 1, 
				share = 1, 
				)
	
	
	def put_last_message(self):
		space = "\n"
		if self.notes:
			self.last_message = ""
			self.last_message = self.last_message + self.transaction_type + space
			self.last_message = self.last_message + space
			self.last_message = self.last_message + _("From : ") + self.edited_user_name + space
			self.last_message = self.last_message + _("To : ")+ self.transaction_to_name + space
			self.last_message = self.last_message + space
			self.last_message = self.last_message + self.transaction_detailed + space
			self.last_message = self.last_message + space
			self.last_message = self.last_message + self.notes + space
			self.last_message = self.last_message + space
			self.last_message = self.last_message + str(now()) + space

	
	def put_messeges(self):
		space = "\n"
		if self.notes:
			if not self.messages:
				self.messages = ""
			self.messages = self.messages + self.transaction_type + space
			self.messages = self.messages + space
			self.messages = self.messages + _("From : ") + self.edited_user_name + space
			self.messages = self.messages + _("To : ") + self.transaction_to_name + space
			self.messages = self.messages + space
			self.messages = self.messages + self.transaction_detailed + space
			self.messages = self.messages + space
			self.messages = self.messages + self.notes + space
			self.messages = self.messages + space
			self.messages = self.messages + str(now()) + space
			self.messages = self.messages + space + ("-"*50) + space
			
			

	def set_indicator(self):
		"""Set indicator for portal"""
		if self.status == "Closed":
			self.response_status = "Closed"
		else:
			if getdate(self.due_date) < getdate(nowdate()):
				self.indicator_color = "red"
				self.indicator_title = "Overdue"
				self.response_status = "Overdue"
			else:
				self.indicator_title = "Waiting"
				self.response_status = "Waiting"
	


	def assign_to_user(self):
		if not self.is_new():
			from frappe.desk.form.assign_to import add
			if self.assign_to == 1:
				if frappe.db.sql("""SELECT `owner`
			FROM `tabToDo`
			WHERE `reference_type`=%(doctype)s
			AND `reference_name`=%(name)s
			AND `status`='Open'
			AND `owner`=%(assign_to)s""", {
				"assign_to": self.transaction_to,
				"doctype": "Administrative Communications",
				"name": self.name
			}):
					frappe.msgprint(_("This Assignment Already in user's To Do list"))
				else:
					add({
				"assign_to": self.transaction_to,
				"doctype": "Administrative Communications",
				"name": self.name,
				"description": self.subject
			})
	

	def add_recipients(self):
		space = "\n"
		if not self.recipients:
			self.recipients = str()
			self.recipients = self.recipients + str(self.edited_user)
		if self.transaction_to:
			if self.transaction_to not in self.recipients:
				self.recipients = self.recipients + space + str(self.transaction_to)


	
	def add_transaction_comment(self):
		if not self.is_new():
			if self.notes or self.transaction_detailed:
				add_comment(
					self.doctype, 
					self.name,
					self.last_message, 
					self.edited_user,
				)


	

	def update_status(self):
		if self.status not in ('Closed') and self.due_date:
			from datetime import datetime
			if self.due_date < datetime.now().date():
				self.db_set('response_status', 'Overdue', update_modified=False)
				

@frappe.whitelist()
def set_overdue(doc, method):
	communications = frappe.get_all("Administrative Communications", filters={'status':['not in',['Closed']]})
	for n in communications:
		if getdate(frappe.db.get_value("Administrative Communications", n.name, "due_date")) > getdate(today()):
			continue
		frappe.get_doc("Administrative Communications", n.name).update_status()