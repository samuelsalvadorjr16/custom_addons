# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.modules.module import get_module_resource

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_payment(models.Model):
	_inherit = "account.payment"

	#This will mark in Charity/ Prize Claim for the Designation of Different Documents for Payment
	pcso_transaction_type = fields.Selection([
	        ('prize_claim','Prize Fund'),
	        ('charity','Charity Fund'),
	    ], index=True, change_default=True,string='PCSO Transaction Type')

	#payment_process_type = fields.Selectiom([('released', 'Date Released'),('released', 'Date Released')])
	date_available = fields.Date('Date Available', track_visibility='onchange')
	date_released = fields.Date('Date Released', track_visibility='onchange')
	date_check_created = fields.Date('Date Check Created')

	@api.multi
	def do_print_checks(self):
		res = super(account_payment, self).do_print_checks()
		if res:
			if self.date_check_created:
				self.write({'date_check_created': fields.Date.today()})


	@api.multi
	def write(self, values):
		model_guarantee = self.env['pcso.transaction']
		#raise Warning(self.pcso_transaction_type)
		if self.pcso_transaction_type == 'charity':
			if values.get('date_available'):
				if self.invoice_ids:
					for invoice in self.invoice_ids:
						if invoice.invoice_line_ids:
							for lines in invoice.invoice_line_ids:
								if lines.guarantee_id:
									obj_pcso_transaction = model_guarantee.search([('id', '=', lines.guarantee_id.id)])
									obj_pcso_transaction.write({'bank': self.journal_id and self.journal_id.bank_id and self.journal_id.bank_id.name or False, 
															    'check_amount': lines.guarantee_approve_amt_rel,
															    'check_number': self.check_number, 
															    'date_check_created': values['date_available']})
		if values.get('date_released'):
				if self.invoice_ids:
					for invoice in self.invoice_ids:
						if invoice.invoice_line_ids:
							for lines in invoice.invoice_line_ids:
								if lines.guarantee_id:
									obj_pcso_transaction = model_guarantee.search([('id', '=', lines.guarantee_id.id)])
									obj_pcso_transaction.write({'is_released': True, 
															    'date_check_created': values['date_released']})


		res=super(account_payment, self).write(values)
		return res