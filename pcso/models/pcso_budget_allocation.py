from odoo import models, fields, api

class PcsoBudgetAllocation(models.Model):
	_name = 'pcso.budget.allocation'
	_description = 'PCSO Budget Allocation'

	name = fields.Char()
	branch_id = fields.Char('Branch ID')
	branch_name = fields.Char('Branch Name')
	alloted_budget = fields.Float('Alloted Budget')
	budget_date = fields.Date('Budget Date')