# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_invoice_line_prize_claim(models.Model):
	_inherit = ["account.invoice.line"]

	@api.one
	@api.depends('first_prize', 'second_prize', 'third_prize', 'third_prize',
				 'fourth_prize', 'fifth_prize', 'jackpot_prize')
	def _compute_prize(self):
		self.price_unit = self.first_prize+ self.second_prize  + self.third_prize  + self.fourth_prize  + self.fifth_prize + self.jackpot_prize


	@api.onchange('first_prize', 'second_prize', 'third_prize', 'third_prize',
				 'fourth_prize', 'fifth_prize', 'jackpot_prize')
	def onchange_amount(self):
	#	if 	self.draw_gametype:
	#		if not self._context.get('jackpot_prize'):
				#if self.draw_gametype.low_tier_product_id:
	#			self.product_id == self.draw_gametype.low_tier_product_id.id
	#		else:
				#if self.draw_gametype.high_tier_product_id:
	#			self.product_id == self.draw_gametype.high_tier_product_id.id
		self.price_unit = self.first_prize+ self.second_prize  + self.third_prize  + self.fourth_prize  + self.fifth_prize + self.jackpot_prize

	@api.onchange('draw_id')
	def onchange_draws(self):
		if not self._context.get('jackpot_prize'):
			if self.draw_id.gametype_id.low_tier_product_id:
				self.product_id = self.draw_id.gametype_id.low_tier_product_id.id
		else:
			if self.draw_id.gametype_id.high_tier_product_id:
				self.product_id = self.draw_id.gametype_id.high_tier_product_id.id

		if self._context.get('branch_id'):
			#raise Warning(self._context.get('branch_id'))
			if self._context.get('transaction_type') == 'prize_claim':
				branch_obj = self.env['config.prize.branch'].search([('id', '=', self._context.get('branch_id'))])
				self.account_analytic_id = branch_obj and branch_obj.analytic_account_id and branch_obj.analytic_account_id.id or False 	


	@api.model
	def _default_product_id(self):
		if self._context.get('transaction_type'):
			if self._context.get('transaction_type') == 'prize_claim':
				return  False #self.env.ref('account_prize_claim_pcso.product_product_prize_claim_cost') #2189 #self.env.ref('account_prize_claim_pcso.product_product_prize_claim_cost_product_template')
			elif self._context.get('transaction_type') == 'charity':
				product_obj = self.env['product.product'].search([('name', '=', 'IMAP'),('default_code', '=', '424-2A1')])
				if product_obj:
					return product_obj.id
				return False
			else:
				return False

	#@api.model
	#def _default_assistance(self):


	@api.model
	def _filter_guarantee_number(self):
		domain = [('state', '=', 'approve'),('is_released', '!=', True)]
		guarantee_number_in_invoice = self.env['account.invoice.line'].search([('guarantee_id', '!=', False)])
		list_guarantee = []
		if guarantee_number_in_invoice:
			for line in guarantee_number_in_invoice:
				list_guarantee.append(line.guarantee_id.id)

			domain.append(('id', 'not in', list_guarantee))


		return domain

	#@api.model
	#def _default_analytic_acc_id(self):
		#if self._context.get('branch_id'):
		#	if self._context.get('transaction_type') == 'charity':
		#		branch_obj = self.env['config.prize.branch'].search([('id', '=', self._context.get('branch_id'))])
		#		#raise Warning(self._context.get('branch_id'))
		#		self.account_analytic_id = branch_obj and branch_obj.analytic_account_id and branch_obj.analytic_account_id.id or False 
	#	return False


	draw_id = fields.Many2one('config.prize.draws', 'Draw ID')
	draw_date = fields.Datetime(related='draw_id.draw_date', string='Draw Date')
	draw_result = fields.Char(related='draw_id.draw_result', string='Draw Result')
	draw_gametype = fields.Many2one('config.prize.gametype',related='draw_id.gametype_id', string='Game Type')
	bettype_id = fields.Many2one('config.prize.bettype', 'Bet Type')
	agency_id = fields.Many2one('config.prize.agency', 'Agency')
	ticket_serial = fields.Char('Ticket Serial')
	jackpot_prize = fields.Float(string='Jackpot Prize', digits=dp.get_precision('Price Claim First Prize'))
	first_prize = fields.Float(string='First Prize', digits=dp.get_precision('Price Claim First Prize'))
	second_prize = fields.Float(string='Second Prize', digits=dp.get_precision('Price Claim Second Prize'))
	third_prize = fields.Float(string='Third Prize', digits=dp.get_precision('Price Claim Third Prize'))
	fourth_prize = fields.Float(string='Fourth Prize', digits=dp.get_precision('Price Claim Fourth Prize'))
	fifth_prize = fields.Float(string='Fifth Prize', digits=dp.get_precision('Price Claim Fifth Prize'))
	prize_amount = fields.Float(string='Prize Amount', compute='_compute_prize')
	#Override Fields
	name = fields.Text(string='Description',required=False)
	price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'),required=True)
	#account_analytic_id = fields.Many2one('account.analytic.account',string='Analytic Account', default=_default_analytic_acc_id)
	# For Charity
	guarantee_id = fields.Many2one('pcso.transaction', string="Guarantee Number", domain=_filter_guarantee_number)
	guarantee_patient_name_rel = fields.Char(related='guarantee_id.patient_name', string='Patient Name')
	guarantee_approve_amt_rel = fields.Float(related='guarantee_id.approved_assistance_amount', string='Approved Amount', digits=dp.get_precision('Charity Assistance Amt'))
	guarantee_assistance_id_rel = fields.Char(related='guarantee_id.assistance_id', string='Assistance ID')
	assistance_id = fields.Many2one('pcso.assistance', string='Assistance') 
	guarantee_number = fields.Char('Guarantee Number')
	patient_name = fields.Char('Patient Name')
	approved_amount = fields.Float(string='Approved Amount', digits=dp.get_precision('Charity Assistance Amt'))

	product_id = fields.Many2one('product.product', string='Product',
	    ondelete='restrict', index=True, default=_default_product_id)

	@api.onchange('guarantee_approve_amt_rel')
	def _approved_amount_onchange(self):
		self.price_unit = self.guarantee_approve_amt_rel or 0

	@api.onchange('guarantee_assistance_id_rel')
	def assistance_onchange(self):
		if self.guarantee_assistance_id_rel:
			assistance_obj=self.env['pcso.assistance'].search([('assistance_id','=', self.guarantee_assistance_id_rel)])
			self.assistance_id = assistance_obj.id or False
		#return False
	@api.onchange('assistance_id')
	def assistanceId_onchange(self):
		if self.assistance_id:
			assistance_obj=self.env['pcso.assistance'].search([('id','=', self.assistance_id.id)])
			self.guarantee_assistance_id_rel = assistance_obj.assistance_id


	@api.onchange('guarantee_id')
	def guarantee_change(self):
		if self.guarantee_id:
			if self._context.get('branch_id'):
				branch_obj = self.env['config.prize.branch'].search([('id', '=', self._context.get('branch_id'))])
				self.account_analytic_id = branch_obj and branch_obj.analytic_account_id and branch_obj.analytic_account_id.id or False 
			if self.guarantee_id:
				self.patient_name = self.guarantee_id.patient_name or False
				self.approved_amount =  self.guarantee_approve_amt_rel or 0.00
				
	@api.multi
	def write(self, values):
		if values.has_key('guarantee_id') and values.get('guarantee_id') !=False:
			guarantee_number_in_invoice = self.env['account.invoice.line'].search([('guarantee_id', '=', values.get('guarantee_id'))])
			if guarantee_number_in_invoice:
				raise Warning('GL %s Already added in Other IMAP Claims.' %(guarantee_number_in_invoice.guarantee_id.name))
		if values.has_key('ticket_serial') and values.has_key('ticket_serial')  !=False:
			ticket_serial_in_invoice = self.env['account.invoice.line'].search([('ticket_serial', '=', values.get('ticket_serial'))])
			if ticket_serial_in_invoice:
				raise  Warning('Ticket No. %s has Already added in Other Prize Claims.' %(ticket_serial_in_invoice[0].ticket_serial))
		return super(account_invoice_line_prize_claim, self).write(values)
	@api.model
	def create(self, values):
		if values.has_key('guarantee_id') and values.get('guarantee_id') !=False:
			guarantee_number_in_invoice = self.env['account.invoice.line'].search([('guarantee_id', '=', values.get('guarantee_id'))])
			if guarantee_number_in_invoice:
				raise Warning('GL %s Already added in Other IMAP Claims.' %(guarantee_number_in_invoice.guarantee_id.name))
		if values.has_key('ticket_serial') and values.has_key('ticket_serial')  !=False:
			ticket_serial_in_invoice = self.env['account.invoice.line'].search([('ticket_serial', '=', values.get('ticket_serial'))])
			if ticket_serial_in_invoice:
				raise  Warning('Ticket No. %s has Already added in Other Prize Claims.' %(ticket_serial_in_invoice[0].ticket_serial))
		return super(account_invoice_line_prize_claim, self).create(values)

	@api.onchange('agency_id')
	def agency_change(self):
		if self.agency_id:
			if self._context.get('transaction_type') == 'prize_claim':
				self.account_analytic_id = self.agency_id and self.agency_id.analytic_account_id  and  self.agency_id.analytic_account_id.id or False
