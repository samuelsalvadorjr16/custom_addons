from odoo import models, fields, api

class PcsoSpecificAssistance(models.Model):
	_name = 'pcso.specific.assistance'
	_description = 'PCSO Specific Assistance'

	name = fields.Char('Specific Assistance')
	specific_assistance_id = fields.Char('Specific Assistance ID')
	assistance_id = fields.Char('Assistance ID')