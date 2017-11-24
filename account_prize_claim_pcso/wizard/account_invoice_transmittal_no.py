# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class voucher_cancel(models.TransientModel):
	_name = 'account.invoice.transmittal_number'


	@api.multi
	def action_create_transmittal_charity_number(self):
		context = dict(self._context or {})
		active_ids = context.get('active_ids', []) or []

		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}

		invoices = self.env['account.invoice'].browse(active_ids)
		invoices_model = self.env['account.invoice']

		for invoice in invoices:
			if invoice.transmittal_charity_number:
				raise UserError(_("Selected IMAP Claim cannot be confirmed as they have already a CPT No."))
				return {'type': 'ir.actions.act_window_close'}

		#Update All The Selected Ids
		#Get the Sequence ID
		seq_str = self.env['ir.sequence'].next_by_code('trans.number.charity') 
		for invoice in invoices:
			invoice.write({'transmittal_charity_number': seq_str})


		return {'type': 'ir.actions.act_window_close'}

	@api.multi
	def action_create_transimittal_account_number(self):
		context = dict(self._context or {})
		active_ids = context.get('active_ids', []) or []

		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		invoices = self.env['account.invoice'].browse(active_ids)

		for invoice in invoices:
			if invoice.transmittal_charity_account_number:
				raise UserError(_("Selected IMAP Claim cannot be confirmed as they have already an APT No."))
				return {'type': 'ir.actions.act_window_close'}
			if invoice.state not in ['approved']:
				raise UserError(_("Selected IMAP Claim cannot be confirmed as they are not yet Approved."))
				return {'type': 'ir.actions.act_window_close'}


		#Update All The Selected Ids
		#Get the Sequence ID
		seq_str = self.env['ir.sequence'].next_by_code('trans.number.acct')
		for invoice in invoices:
			invoice.write({'transmittal_charity_account_number': seq_str})



		return {'type': 'ir.actions.act_window_close'}

