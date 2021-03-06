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
	analytic_account_id = fields.Many2one('account.analytic.account', 'Cost Ctr/Dept')

class prize_config_transaction_type(models.Model):
	_name = 'config.prize.transactiontype'

	name = fields.Char('Name')

class prize_config_agency(models.Model):
	_name = "config.prize.agency"

	_rec_name = 'agency_id'
	name = fields.Char('Name')
	agency_id = fields.Char('Agency ID')
	owner_id = fields.Many2one('res.partner', 'Owner')
	analytic_account_id =  fields.Many2one('account.analytic.account', 'Cost Ctr/Dept')


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
			res_agency_obj = self.env['config.prize.agency'].search([('id', '=', res_id.id)])
			res_agency_obj.write({'owner_id': res_partner_id.id})			
		return res_id

	@api.multi
	def name_get(self):
		result=[]
		context = self._context or {}
		for record in self:
			result.append((record.id, '[' + record.agency_id + '] ' + record.name))
		return result


class prize_config_gametype(models.Model):
	_name = 'config.prize.gametype'

	name = fields.Char('Name')
	id_char = fields.Char('Game Type ID')

	jackpot_product_id = fields.Many2one('product.product', string="Jackpot")
	high_tier_product_id = fields.Many2one('product.product', string="High Tier")
	low_tier_product_id = fields.Many2one('product.product', string="Low Tier")

	default_jackpot_account_id = fields.Many2one('account.account', string="Account Jackpot")
	default_high_tier_account_id = fields.Many2one('account.account', string="Account High Tier")
	default_low_tier_account_id = fields.Many2one('account.account', string="Account Low Tier")

class prize_config_bettype(models.Model):
	_name = 'config.prize.bettype'

	name = fields.Char('Name')
	id_char = fields.Char('Bet Type ID')

class prize_config_draws(models.Model):
	_name = "config.prize.draws"
	_rec_name='drawid'

	drawid = fields.Char('Draw ID')
	draw_date = fields.Datetime('Draw Date')
	draw_result = fields.Char('Draw Result')
	gametype_id = fields.Many2one('config.prize.gametype', 'Game Type')
	jackpot_prize = fields.Float(string='Jackpot Prize', digits=dp.get_precision('Price Claim First Prize'))
	first_prize = fields.Float(string='First Prize', digits=dp.get_precision('Price Claim First Prize'))
	second_prize = fields.Float(string='Second Prize', digits=dp.get_precision('Price Claim Second Prize'))
	third_prize = fields.Float(string='Third Prize', digits=dp.get_precision('Price Claim Third Prize'))
	fourth_prize = fields.Float(string='Fourth Prize', digits=dp.get_precision('Price Claim Fourth Prize'))
	fifth_prize = fields.Float(string='Fifth Prize', digits=dp.get_precision('Price Claim Fifth Prize'))	

class charity_config_checklist_doc(models.Model):
	_name = "config.charity.documents"
	_rec_name='attachment_id'

	attachment_id = fields.Char('Attachment ID', required=True)
	name = fields.Char('Description', required=True)

	document_attachment_ids = fields.One2many('config.charity.docs.attachlist', 'document_id', string='Attachments')
	@api.multi
	def name_get(self):
		result=[]
		context = self._context or {}
		for record in self:
			result.append((record.id, '[' + record.attachment_id + '] ' + record.name))
		return result

class charity_config_checklist_doc_att_list(models.Model):
	_name = 'config.charity.docs.attachlist'
	_order ='document_id,sequence,id'

	sequence = fields.Integer('Sequence', default=10)
	name = fields.Char(related='attachment_id.name')
	document_id = fields.Many2one('config.charity.documents', 'Charity Document')
	attachment_id = fields.Many2one('config.charity.docs.attachtype', 'Attachment Type', required=True)

class charity_config_checklist_doc_attachment(models.Model):
	_name = 'config.charity.docs.attachtype'

	name = fields.Char('Attachment Title', required=True)
	active = fields.Boolean('Active', default=True)