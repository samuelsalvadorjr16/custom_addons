# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.modules.module import get_module_resource

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class purchase_order(models.Model):
	_inherit = ["purchase.order"]

	is_from_rfp = fields.Boolean('From Request for Payment', default=False)
	state = fields.Selection([
	    ('draft', 'RFQ'),
	    ('sent', 'RFQ Sent'),
	    ('submit', 'Submitted'),
	    ('approved', 'Approved'),	    
	    ('denied', 'Denied'),
	    ('to approve', 'To Approve'),
	    ('purchase', 'Purchase Order'),
	    ('to_invoiced', 'To Invoice'),
	    ('done', 'Locked'),
	    ('cancel', 'Cancelled')
	    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
	approve_uid = fields.Many2one('res.users', 'Approved By')
	submitted_uid = fields.Many2one('res.users', 'Submitted By')
	denied_uid = fields.Many2one('res.users', 'Denied By')

	@api.multi
	def action_submit_rfp(self):
		return self.write({'state': 'submit', 'submitted_uid': self._uid})

	@api.multi
	def action_approved_rfp(self):
		return  self.write({'state': 'approved', 'approve_uid': self._uid})

	@api.multi
	def action_deny_rfp(self):
		return  self.write({'state': 'denied', 'denied_uid': self._uid})
