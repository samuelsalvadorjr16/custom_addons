# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class voucher_cancel(models.TransientModel):
	_name = 'account.voucher.cancel'

	reason = fields.Text('Reason')
	@api.multi
	def action_return(self):
		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		inv = self.env['account.invoice'].browse(self._context['active_id'])
		reason = self.reason
		inv.action_set_to_return(reason)
		return {'type': 'ir.actions.act_window_close'}

	def action_cancel(self):
		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		inv = self.env['account.invoice'].browse(self._context['active_id'])
		reason = self.reason
		inv.action_set_to_cancel(reason)
		return {'type': 'ir.actions.act_window_close'}

	def action_return_rfp(self):
		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		inv = self.env['purchase.order'].browse(self._context['active_id'])
		reason = self.reason
		inv.action_return_rfp(reason)
		return {'type': 'ir.actions.act_window_close'}
		
	def action_cancel_rfp(self):
		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		inv = self.env['purchase.order'].browse(self._context['active_id'])
		reason = self.reason
		inv.action_deny_rfp(reason)
		return {'type': 'ir.actions.act_window_close'}		


	def action_return_opex(self):
		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		inv = self.env['account.invoice'].browse(self._context['active_id'])
		reason = self.reason
		res = inv.action_set_to_return(reason)
		if res and inv.origin:
			rfp_obj = self.env['purchase.order'].search([('name', '=', inv.origin)])
			if rfp_obj:
				rfp_obj.action_return_rfp('RETURN FROM OPEX \n' + reason)
		return {'type': 'ir.actions.act_window_close'}

	def action_cancel_opex(self):
		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		inv = self.env['account.invoice'].browse(self._context['active_id'])
		reason = self.reason
		res = inv.action_set_to_cancel(reason)
		if res and inv.origin:
			rfp_obj = self.env['purchase.order'].search([('name', '=', inv.origin)])
			if rfp_obj:
				rfp_obj.action_return_rfp('CANCELLED FROM OPEX \n' + reason)	
					
		return {'type': 'ir.actions.act_window_close'}
