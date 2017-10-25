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
				 'fourth_prize', 'fifth_prize')
	def _compute_prize(self):
		self.price_unit = self.first_prize+ self.second_prize  + self.third_prize  + self.fourth_prize  + self.fifth_prize 

	@api.model
	def _default_product_id(self):
		if self._context.get('transaction_type'):
			if self._context.get('transaction_type') == 'prize_claim':
				return self.env.ref('account_prize_claim_pcso.product_product_prize_claim_cost')
			else:
				return False

	draw_id = fields.Many2one('config.prize.draws', 'Draw ID')
	draw_date = fields.Datetime(related='draw_id.draw_date', string='Draw Date')
	draw_result = fields.Char(related='draw_id.draw_result', string='Draw Date')
	draw_gametype = fields.Many2one('config.prize.gametype',related='draw_id.gametype_id', string='Game Type')
	bettype_id = fields.Many2one('config.prize.bettype', 'Bet Type')
	agency_id = fields.Many2one('config.prize.agency', 'Agency')
	ticket_serial = fields.Char('Ticket Serial')
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
	guarantee_number = fields.Char('Guarantee Number')

	product_id = fields.Many2one('product.product', string='Product',
	    ondelete='restrict', index=True, default=_default_product_id)