from odoo import models, fields, api

class PcsoBranch(models.Model):
	_name = 'pcso.branch'
	_description = 'PCSO Branch'

	name = fields.Char('Branch Name')
	branch_id = fields.Char('Branch ID')
	is_head_office = fields.Boolean('Is Head Office')
	address = fields.Text('Address')
	cmid = fields.Char('CMID')