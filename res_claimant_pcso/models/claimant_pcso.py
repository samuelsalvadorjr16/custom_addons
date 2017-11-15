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
		('DL',"Driver's License"),
		('PS','Passport'),
		('PA','Postal ID'),
		('BR','Barangay ID'),
		('CO','Company ID'),
		('PRC','PRC ID'),
		('NBI','NBI'),
		('PC','Police Clearance'),
		('GSIS','GSIS ID'),
		('OWWA','OWWA ID'),
		('OFW','OFW ID'),
		('SB',"Seafarer's Book"),
		('ACR','Alien / Immigration Cert'),
		('GOVT','Government ID'),
		('DSWD','DSWD Cert'),
		('FAL','Firearm License'),
		('PHC','Phil Health Card'),
		('SSS','SSS'),
		('TIN','TIN'),
		('OSCA','OSCA'),
		('PCSO AGENT ID','PCSO ID'),
		('HDMF','HDMF ID'),
		('DSWD4Ps','DSWD4Ps'),
		('AFP','AFP ID'),
		('PNP','PNP ID'),
		('UMID','UMID'),
		('PWD','PWD'),
		('VOTERSID','Voters ID'),

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


