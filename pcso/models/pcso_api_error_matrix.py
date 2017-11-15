from odoo import models, fields, api

class PcsoApiErrorMatrix(models.Model):
	_name = 'pcso.api.error.matrix'
	_description = 'PCSO API Error Matrix'

	code = fields.Char()
	message = fields.Char()
	type = fields.Char()