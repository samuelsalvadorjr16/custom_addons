# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class prize_config_branch(models.Model):
	_name = 'config.prize.branch'
	
	name = fields.Char('Name')

class prize_config_transaction_type(models.Model):
	_name = 'config.prize.transactiontype'

	name = fields.Char('Name')

class prize_config_agency(models.Model):
	_name = "config.prize.agency"

	name = fields.Char('Name')
	agency_id = fields.Char('ID')
	owner_id = fields.Many2one('res.partner', 'Owner')


	@api.model
	def create(self, vals):
		res_id = super(prize_config_agency, self).create(vals)
		# Create an Owner
		if res_id:
			res_partner_obj = self.env['res.partner']
			res_partner_id =res_partner_obj.create({
				'company_type': 'individual',
				'name': vals['name'] + ' [' + vals['agency_id'] +']',
				'company_type': 'individual',
				'customer': True,
				'supplier': True,})
			res_agency_obj = self.env['config.prize.agency'].search([('id', '=', res_id)])
			res_agency_obj.write({'owner_id': res_partner_id})			
		return res_id


class prize_config_gametype(models.Model):
	_name = 'config.prize.gametype'

	name = fields.Char('Name')
	id_char = fields.Char('ID')

class prize_config_bettype(models.Model):
	_name = 'config.prize.bettype'

	name = fields.Char('Name')
	id_char = fields.Char('ID')

class prize_config_draws(models.Model):
	_name = "config.prize.draws"
	_rec_name='drawid'

	drawid = fields.Char('Draw ID')
	draw_date = fields.Datetime('Draw Date')
	draw_result = fields.Char('Draw Result')
	gametype_id = fields.Many2one('config.prize.gametype', 'Game Type')
	first_prize = fields.Float(string='First Prize', digits=dp.get_precision('Price Claim First Prize'))
	second_prize = fields.Float(string='Second Prize', digits=dp.get_precision('Price Claim Second Prize'))
	third_prize = fields.Float(string='Third Prize', digits=dp.get_precision('Price Claim Third Prize'))
	fourth_prize = fields.Float(string='Fourth Prize', digits=dp.get_precision('Price Claim Fourth Prize'))
	fifth_prize = fields.Float(string='Fifth Prize', digits=dp.get_precision('Price Claim Fifth Prize'))	