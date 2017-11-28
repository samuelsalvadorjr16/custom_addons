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

	@api.model
	def _filter_journal_id(self):
		#return_val =[]
		return_val = ['&',('type', 'in', ('bank', 'cash'))]
		if self._context.get('transaction_type') == 'prize_claim':
			return_val.append(('name', 'ilike','PRF'))
		elif self._context.get('transaction_type') == 'charity':
			return_val.append(('name', 'ilike','CHF'))
		else:
			return_val.append(('name', 'ilike','OPF'))
		#for x in self._context:
		#	_logger.info(x)
		#raise Warning(return_val)
		return return_val


	#This will mark in Charity/ Prize Claim for the Designation of Different Documents for Payment
	pcso_transaction_type = fields.Selection([
	        ('prize_claim','Prize Fund'),
	        ('charity','Charity Fund'),
	    ], index=True, change_default=True,string='PCSO Transaction Type')

	#payment_process_type = fields.Selectiom([('released', 'Date Released'),('released', 'Date Released')])
	date_available = fields.Date('Date Available', track_visibility='onchange')
	date_released = fields.Date('Date Released', track_visibility='onchange')
	date_check_created = fields.Date('Date Check Created')
	or_number = fields.Char('OR Number', size=50)
	or_date = fields.Date('OR Date')
	journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=_filter_journal_id)






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

	@api.multi
	def post(self):
		""" Create the journal items for the payment and update the payment's state to 'posted'.
		A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
		and another in the destination reconciliable account (see _compute_destination_account_id).
		If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
		If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
		Override ***** THE FOLLOWING
		"""
		
		for rec in self:
			if rec.state != 'draft':
				raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)		
			if any(inv.state not in ['open', 'approved'] for inv in rec.invoice_ids):
				raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
			if rec.payment_type == 'transfer':
				sequence_code = 'account.payment.transfer'
			else:
				if rec.partner_type == 'customer':
					if rec.payment_type == 'inbound':
						sequence_code = 'account.payment.customer.invoice'
					if rec.payment_type == 'outbound':
						sequence_code = 'account.payment.customer.refund'
				if rec.partner_type == 'supplier':
				 	if rec.payment_type == 'inbound':
				 		sequence_code = 'account.payment.supplier.refund'
				 	if rec.payment_type == 'outbound':
				 		sequence_code = 'account.payment.supplier.invoice'
			rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
			if not rec.name and rec.payment_type != 'transfer':
				raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
			amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
			move = rec._create_payment_entry(amount)
			if rec.payment_type == 'transfer':
				transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
				transfer_debit_aml = rec._create_transfer_entry(amount)
				(transfer_credit_aml + transfer_debit_aml).reconcile()
			rec.write({'state': 'posted', 'move_name': move.name})
