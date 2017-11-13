# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.modules.module import get_module_resource
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class purchase_order(models.Model):
	_inherit = ["purchase.order"]

	@api.model
	def _get_states(self):
		if self._context.get('default_is_from_rfp'):
			return 'draft_rfq'
		else:
			return 'draft'

	is_from_rfp = fields.Boolean('From Request for Payment', default=False)
	state = fields.Selection([
	    ('draft', 'RFQ'),
	    ('draft_rfq', 'Draft'),
	    ('return', 'Returned'),
	    ('sent', 'RFQ Sent'),
	    ('submit', 'Submitted'),
	    ('approved', 'Approved'),	    
	    ('denied', 'Denied'),
	    ('to approve', 'To Approve'),
	    ('purchase', 'Purchase Order'),
	    ('to_invoiced', 'To Invoice'),
	    ('done', 'Locked'),
	    ('cancel', 'Cancelled')
	    ], string='Status', readonly=True, index=True, copy=False, default=_get_states, track_visibility='onchange')

	status_history = fields.Text('History', copy=False)


	@api.model
	def _get_job(self):
		return self.env.user.job_id.id

	@api.model
	def _get_department(self):
		return self.env.user.department_id.id

	@api.model
	def _get_costcenter(self):
		if self.department_id:
			return self.department_id.account_analytic_id.id
		else:
			return self.env.user.department_id.account_analytic_id.id

	@api.onchange('analytic_account_id')
	def _onchange_ann_acc(self):
		#raise Warning(self.order_line.product_id)
		for inv in self.order_line:
			inv.account_analytic_id = self.analytic_account_id.id
			#_logger.info(inv.product_id)

	create_uid_department_id = fields.Many2one('hr.department', related='create_uid.department_id', string="Created User Department")
	create_uid_job_id = fields.Many2one('hr.job', related='create_uid.job_id', string="Created User Job")
	department_id = fields.Many2one('hr.department', string="Default Department", default=_get_department)
	analytic_account_id = fields.Many2one('account.analytic.account', string="Cost Center/Department", default=_get_costcenter) #, default=_get_costcenter
	job_id = fields.Many2one('hr.job', string="Default Job", default=_get_job)
	approve_uid = fields.Many2one('res.users', 'Approved By')
	submitted_uid = fields.Many2one('res.users', 'Submitted By')
	denied_uid = fields.Many2one('res.users', 'Denied By')

	#OVERRIDES METHODS
	@api.depends('state', 'order_line.qty_invoiced', 'order_line.qty_received', 'order_line.product_qty')
	def _get_invoiced(self):
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		for order in self:
			if order.state not in ('purchase', 'done', 'approved'):
				order.invoice_status = 'no'
				continue

			if any(float_compare(line.qty_invoiced, line.product_qty if line.product_id.purchase_method == 'purchase' else line.qty_received, precision_digits=precision) == -1 for line in order.order_line):
				order.invoice_status = 'to invoice'
			elif all(float_compare(line.qty_invoiced, line.product_qty if line.product_id.purchase_method == 'purchase' else line.qty_received, precision_digits=precision) >= 0 for line in order.order_line) and order.invoice_ids:
				order.invoice_status = 'invoiced'
			else:
				order.invoice_status = 'no'
	@api.multi
	def button_confirm(self):
		for order in self:
			if order.state not in ['draft', 'sent','submit', 'approved']:
				continue
			
			order._add_supplier_to_product()
			# Deal with double validation process
			if order.company_id.po_double_validation == 'one_step'\
			or (order.company_id.po_double_validation == 'two_step'\
			and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
			or order.user_has_groups('purchase.group_purchase_manager'):
				order.button_approve()
			else:
				order.write({'state': 'to approve'})
		return True



	@api.multi
	def action_submit_rfp(self):
		stats_his =''
		if self.status_history:
			stats_his = self.status_history
		state_dict ={'state': 'submit', 'submitted_uid': self._uid,
	    	 'status_history': 'SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''}
		if self.state == 'draft_rfq':
			state_dict['status_history'] = 'SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''
		elif self.state == 'return':
			state_dict['status_history'] = 'RE-SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''
		return self.write(state_dict)

	@api.multi
	def action_approved_rfp(self):
		stats_his=''
		self.button_confirm()
		if self.status_history:
			stats_his = self.status_history
		return  self.write({'state': 'approved', 'approve_uid': self._uid,'status_history': 'APPROVED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''})

	@api.multi
	def action_deny_rfp(self, reason):
		return  self.write({'state': 'denied', 'denied_uid': self._uid, 
							'status_history': 'DENIED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n *****REASON \n' + reason  + '\n' + self.status_history})

	@api.multi
	def action_return_rfp(self, reason):
		return  self.write({'state': 'return',
							'status_history': 'RETURNED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n *****REASON \n' + reason  + '\n' + self.status_history})
	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			if self._context.get('default_is_from_rfp'):
				vals['name'] = self.env['ir.sequence'].next_by_code('request.payment.seq') or '/'
			else:
				vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
		#raise Warning(vals['name'])
		return super(purchase_order, self).create(vals)

class purchase_order_line(models.Model):
	_inherit='purchase.order.line'

	@api.model
	def _get_def_ann_acc(self):
		if self._context.get('analytic_account_id'):
			branch_obj = self.env['account.analytic.account'].search([('id', '=', self._context.get('analytic_account_id'))])
			return branch_obj.id

	account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', default=_get_def_ann_acc)