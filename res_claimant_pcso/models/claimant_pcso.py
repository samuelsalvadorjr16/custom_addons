# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


_logger = logging.getLogger(__name__)

class res_partner_claimant(models.Model):
	#_name = 'res.claimant.pcso'
	_inherit = "res.partner"

	partner_claimant = fields.Boolean('Claimant?')
	first_name = fields.Char('First Name(Pangalan)')
	last_name = fields.Char('Last Name(Apelyido)')
	middle_name = fields.Char('Middle Name(Gitnang Pangalan)')
	province = fields.Char('Province')
	birthdate = fields.Date('Birthday')
	id_number = fields.Char('ID Number')
	id_type = fields.Selection([
		('voters', 'Voters ID'),
		('passport', 'Passport'),
		('phic_id', 'Philhealth'),
		('sss_id', 'SSS ID'),
		('postal_id', 'Postal ID'),
		],string='ID Type')
	gender = fields.Selection([
	    ('male', 'Male'),
	    ('female', 'Female'),
	], string="Gender")
	civil_status = fields.Selection([
	    ('single', 'Single'),
	    ('married', 'Married'),
	    ('widower', 'Widow(er)'),
	    ('divorced', 'Divorced'),
	    ('annuled', 'Annuled')
	], string='Civil Status')

	@api.onchange('first_name', 'last_name', 'middle_name')
	def name_change(self):
		first_name = ''
		last_name = ''
		middle_name = ''

		if not self.first_name:
			self.first_name = ''
		if not self.last_name:
			self.last_name = ''
		if not self.middle_name:
			self.middle_name = ''

		self.name = self.first_name + ' ' + self.middle_name + ' ' + self.last_name					


