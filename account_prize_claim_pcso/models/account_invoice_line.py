# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

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
			#raise Warning(self._context.get('transaction_type'))
			if self._context.get('transaction_type') == 'prize_claim':
				#raise Warning(self.env.ref('account_prize_claim_pcso.product_product_prize_claim_cost'))
				return  self.env.ref('account_prize_claim_pcso.product_product_prize_claim_cost') #2189 #self.env.ref('account_prize_claim_pcso.product_product_prize_claim_cost_product_template')
			elif self._context.get('transaction_type') == 'charity':
				product_obj = self.env['product.product'].search([('name', '=', 'IMAP'),('default_code', '=', '424-2A1')])
				if product_obj:
					return product_obj.id
				return False
				#return  self.env.ref('account_prize_claim_pcso.product_product_prize_claim_cost')
			else:
				return False

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
	# For Charity
	guarantee_id = fields.Many2one('pcso.transaction', string="Guarantee Number")
	guarantee_patient_name_rel = fields.Char(related='guarantee_id.patient_name', string='Patient Name')
	guarantee_approve_amt_rel = fields.Float(related='guarantee_id.approved_assistance_amount', string='Approved Amount', digits=dp.get_precision('Charity Assistance Amt'))
	guarantee_number = fields.Char('Guarantee Number')
	patient_name = fields.Char('Patient Name')
	approved_amount = fields.Float(string='Approved Amount', digits=dp.get_precision('Charity Assistance Amt'))

	product_id = fields.Many2one('product.product', string='Product',
	    ondelete='restrict', index=True, default=_default_product_id)

	@api.onchange('approved_amount')
	def _approved_amount_onchange(self):
		self.price_unit = self.approved_amount

	@api.onchange('guarantee_id')
	def guarantee_change(self):
		#Check Guarantee Number
		#raise Warning(111)
		#if self.guarantee_number:
		#	pcso_obj =self.env['pcso.transaction'].search([('name', '=', self.guarantee_number)])
		#	if pcso_obj:
		#		raise Warning(pcso_obj)
		#		self.guarantee_id = pcso_obj.id
				#self.patient_name = self.guarantee_id.patient_name or 0.00
				#self.approved_amount = self.guarantee_id.approved_assistance_amount or 0.00
		#	else:
		#		raise Warning('Guarantee Number Not Define')
		if self.guarantee_id:
			self.patient_name = self.guarantee_id.patient_name or False
			self.approved_amount =  self.guarantee_approve_amt_rel or 0.00
		#elif not self.guarantee_id:
		#	self.approved_amount = 0.00
