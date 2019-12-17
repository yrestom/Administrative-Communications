from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Administrative Communications"),
			"items": [
				{
					"type": "doctype",
					"name": "Administrative Communications",
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Communications Type",
				},
				{
					"type": "doctype",
					"name": "Transaction Detailed",
				},
				
			]
		},
		
		
	]
