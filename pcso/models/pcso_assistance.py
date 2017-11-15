from odoo import models, fields, api

class PcsoAssistance(models.Model):
	_name = 'pcso.assistance'
	_description = 'PCSO Assistance'

	name = fields.Char('Assistance')
	assistance_id = fields.Char('Assistance ID')
	# parent_id = fields.Char('Parent ID')