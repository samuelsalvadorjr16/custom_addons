from odoo import models, fields, api

class PcsoTransaction(models.Model):
	_name = 'pcso.transaction'
	_description = 'PCSO Transaction'

	# name = fields.Char(compute='compute_name', readonly=True, store=True, track_visibility='always')
	name = fields.Char('GL Number')
	applicant_id = fields.Char('Applicant ID')
	application_id = fields.Char('Application ID')
	patient_name = fields.Char('Patient Name')
	assistance_id = fields.Char('Assistance ID') # Many2one
	specific_assistance_id = fields.Char('Specific Assistance ID') # Many2one
	approved_assistance_amount = fields.Float('Approved Assistance Amount')
	medical_institution_id = fields.Char('Medical Institution ID') # Many2one
	branch_id = fields.Char('Branch ID')
	application_date = fields.Datetime('Application Date')
	date_approved = fields.Datetime('Date Approved')
	transaction_code = fields.Char('Transaction Code')

	# FOR REVERSAL
	reverse_transaction = fields.Selection([
		('expired', 'Expired Guarantee Letter'),
		('appealed', 'Appealed Assistance Amount'),
	], string='Reverse Transaction')
	reverse_reason = fields.Text('Reverse Reason')
	reverse_date = fields.Datetime('Reverse Date')

	# FOR CHECK INQUIRY AND STATUS
	check_number = fields.Char('Check Number')
	bank = fields.Char()
	check_amount = fields.Float('Check Amount')
	date_check_created = fields.Datetime('Check Created')
	is_released = fields.Boolean()
	date_released = fields.Datetime()

	state = fields.Selection([
		('approve', 'Approved'),
		('cancel', 'Canceled'),
	], default='approve')

	# @api.depends('gl_number')
	# def compute_name(self):
	# 	self.name = self.gl_number
