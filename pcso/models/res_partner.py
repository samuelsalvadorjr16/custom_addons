from odoo import models, fields, api

class ResPartner(models.Model):
	_inherit = 'res.partner'

	vat = fields.Char('Tax ID')