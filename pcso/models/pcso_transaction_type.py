from odoo import models, fields, api

class PcsoTransactionType(models.Model):
	_name = 'pcso.transaction.type'
	_description = 'PCSO Transaction Type'

	name = fields.Char('Transaction Type Name')
	code = fields.Char('Transaction Code')