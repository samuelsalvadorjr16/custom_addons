# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class check_validation_cancel(models.TransientModel):
	_name = 'account.payment.check.cancel'

	reason = fields.Text('Reason')
	@api.multi
	def action_confirm(self):
		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		inv = self.env['account.payment'].browse(self._context['active_id'])
		reason = self.reason
		inv.action_confirm(reason)
		return {'type': 'ir.actions.act_window_close'}

	@api.multi
	def action_cancel_confirm(self):
		if not self._context.get('active_id'):
			return {'type': 'ir.actions.act_window_close'}
		inv = self.env['account.payment'].browse(self._context['active_id'])
		reason = self.reason
		inv.action_cancel_check_confirm(reason)
		return {'type': 'ir.actions.act_window_close'}	
