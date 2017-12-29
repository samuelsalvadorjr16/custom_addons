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

	#For Report Purposes
	request_number = fields.Char(related='invoice_id.draft_number_sequence', string='Request Number')
	request_date = fields.Datetime(related='invoice_id.create_date', string='Request Date')
	soa_request_date = fields.Date(related='invoice_id.date_received', string='SOA Date')
	transmittal_number_charity = fields.Char(related='invoice_id.transmittal_charity_number', string='Transmittal No.')
	voucher_number = fields.Char(related='invoice_id.number', string='Voucher Number')
	voucher_date = fields.Date(related='invoice_id.date_received', string='Voucher Date')
	invoice_state = fields.Selection(related='invoice_id.state', string='Status')
	depart_approve_date= fields.Date(related='invoice_id.certified_correct_date', string='DM Approved Date')
	gm_agm_approve_date= fields.Date(related='invoice_id.approve_date', string='GM/AGM Approved Date')
	payment_ids = fields.Many2many(related='invoice_id.payment_ids', string='Payments')

	cheque_number = fields.Integer(related='payment_ids.check_number', string='Cheque Number')
	cheque_date = fields.Date(related='payment_ids.date_available', string='Cheque Date')
	cheque_or_number = fields.Char(related='payment_ids.or_number', string='OR Number')
	cheque_or_date = fields.Date(related='payment_ids.or_date', string='OR Date')
	#TAX
	tax_one_percent = fields.Monetary(string='Tax 1 Percent', currency_field='company_currency_id',store=True, readonly=True, compute='_compute_tax')
	tax_two_percent = fields.Monetary(string='Tax 2 Percent', currency_field='company_currency_id',store=True, readonly=True, compute='_compute_tax')
	tax_three_percent = fields.Monetary(string='Tax 3 Percent', currency_field='company_currency_id',store=True, readonly=True, compute='_compute_tax')
	tax_five_percent = fields.Monetary(string='Tax 5 Percent', currency_field='company_currency_id',store=True, readonly=True, compute='_compute_tax')
	net_amount = fields.Monetary(string='Net Amount', currency_field='company_currency_id',store=True, readonly=True, compute='_compute_tax')

	gl_year = fields.Integer(string='GL Year', compute='_compute_year_gl', store=True)

	#move_id
	@api.one
	@api.depends('voucher_date')
	def _compute_year_gl(self):
		if self.voucher_date:
			self.gl_date = fields.Date.from_string(self.voucher_date).year

	@api.one
	@api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice')
	def _compute_tax(self):
		for tax in self.invoice_line_tax_ids:
			if tax.amount == 1.0:
				if tax.amount_type == 'base_price':
					if tax.is_custom_price_included == True:
						base_amount = round(self.price_unit / 1.12,5)
					else:
						base_amount = self.price_unit
					self.tax_one_percent = (base_amount * (tax.amount/100))
			elif tax.amount == 2.0:
				if tax.amount_type == 'base_price':
					if tax.is_custom_price_included == True:
						base_amount = round(self.price_unit / 1.12,5)
					else:
						base_amount = self.price_unit
					self.tax_two_percent = (base_amount * (tax.amount/100))
			elif tax.amount == 3.0:
				if tax.amount_type == 'base_price':
					if tax.is_custom_price_included == True:
						base_amount = round(self.price_unit / 1.12,5)
					else:
						base_amount = self.price_unit
					self.tax_three_percent = (base_amount * (tax.amount/100))
			elif tax.amount == 5.0:
				if tax.amount_type == 'base_price':
					if tax.is_custom_price_included == True:
						base_amount = round(self.price_unit / 1.12,5)
					else:
						base_amount = self.price_unit
					self.tax_five_percent = (base_amount * (tax.amount/100))
			self.net_amount = self.price_unit - (self.tax_one_percent + self.tax_five_percent)
		if self.net_amount <=0:
			self.net_amount = self.price_unit






	
	@api.multi
	def get_tax_one_percent(self):
		self.ensure_one()
		for tax in self.invoice_line_tax_ids:
			if tax.amount == 1.0:
				if tax.amount_type == 'base_price':
					if tax.is_custom_price_included == True:
						base_amount = round(self.price_unit / 1.12,5)
						return (base_amount * (tax.amount/100) )
					else:
						base_amount = self.price_unit
						return (base_amount * (tax.amount/100))
		return 0.00

	@api.multi
	def get_tax_three_or_five_percent(self):
		self.ensure_one()
		for tax in self.invoice_line_tax_ids:
			if tax.amount in [3.0, 5.0] :
				if tax.amount_type == 'base_price':
					if tax.is_custom_price_included == True:
						base_amount = round(self.price_unit / 1.12,5) 
						return (base_amount * (tax.amount/100))
					else:
						base_amount = self.price_unit
						return (base_amount * (tax.amount/100))
		return 0.00

	@api.multi
	def get_net_per_line(self):
		self.ensure_one()
		one_tax_percent = self.get_tax_one_percent()
		other_tax_percent = self.get_tax_three_or_five_percent()
		return self.price_subtotal - (one_tax_percent + other_tax_percent)


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
			#Get Default Taxes
			#fiscal_postion_ids = self.env['account.fiscal.position'].search([('id','=', self.partner_id.property_account_position_id.id)])
			account_tax = self.env['account.tax'].browse()
			for tax in self.partner_id.tax_ids:
				if tax.tax_type == self.assistance_id.tax_type:
					account_tax |=  tax
			self.invoice_line_tax_ids = account_tax


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
