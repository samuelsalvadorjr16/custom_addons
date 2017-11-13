# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo import tools, _
from odoo.modules.module import get_module_resource

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)

class account_invoice_prize_claim(models.Model):
	_inherit = ["account.invoice"]

	partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
	    required=True, readonly=True, states={'draft': [('readonly', False)]},
	    track_visibility='always')

	branch_id = fields.Many2one('config.prize.branch', string='Branch', readonly=True, states={'draft': [('readonly', False)]})
	#transaction_id = fields.Many2one('config.prize.transactiontype', string='Transaction Type')
	draft_number_sequence = fields.Char(String='Number',default=lambda self: _('New Voucher'))

	claimant_id = fields.Many2one('res.partner', string='Claimant')
	claimant_type_id = fields.Selection(related='partner_id.id_type', string='ID Type')
	claimant_id_number = fields.Char(related='partner_id.id_number', string='ID Number', store=True)
	claimant_gender = fields.Selection(related='partner_id.gender', string='Gender', store=True)
	claimant_occupation = fields.Char( related='partner_id.function', string='Occupation', store=True)
	claimant_birthdate = fields.Date( related='partner_id.birthdate', string='Birthday', store=True)
	remarks = fields.Text('Remarks')
	transaction_date = fields.Date('Transaction Date', default=fields.Date.context_today)
	jackpot_prize = fields.Boolean('Jackpot Winner', readonly=True, states={'draft': [('readonly', False)]})
	analytic_account_id = fields.Many2one('account.analytic.account', string="Cost Center/Department")

	write_date = fields.Datetime('Write Date', track_visibility='always', copy=True)
	transaction_type = fields.Selection([
	        ('prize_claim','Prize Fund'),
	        ('charity','Charity Fund'),
	    ], index=True, change_default=True,string='Transaction Type')

	#type = fields.Selection([
	#        ('out_invoice','Customer Invoice'),
	#        ('in_invoice','Vendor Bill'),
	#        ('out_refund','Customer Credit Note'),
	#        ('in_refund','Vendor Credit Note'),
	#        ('in_prizeclaim_invoice','Prize Claim'),
	#        ('in_charityfund_invoice','Charity Fund'),
	#    ], readonly=True, index=True, change_default=True,
	#    default=lambda self: self._context.get('type', 'out_invoice'),
	#    track_visibility='always')

	state = fields.Selection([
	        ('draft','Draft'),
	        ('return','Return'),
	        ('submit', 'Submitted'),
	        ('under_review', 'Under Review'),
	        ('under_2nd_review', '2nd Review'),
	        ('for_approval', 'For Approval'),
	        ('approved', 'Approved'),
	        ('denied', 'Denied'),	        
	        ('open', 'Open'),
	        ('paid', 'Paid'),
	        ('cancel', 'Cancelled'),
	    ], string='Status', index=True, readonly=True, default='draft',
	    track_visibility='onchange', copy=False,
	    help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
	         " * The 'Pro-forma' status is used when the invoice does not have an invoice number.\n"
	         " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
	         " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
	         " * The 'Cancelled' status is used when user cancel invoice.\n"
	         " * The 'Submitted' status is used when user submitted a draft Prize Claim.\n"
	         " * The 'Approved' status is used when user approved a submitted Prize Claim\n."
	         " * The 'Denied' status is used when user denied a submitted Prize Claim.")

	#reviewing_state =fields.Selection([('under_review_prze_approved_lv_1', 'Under Review Aprrove Level 1'),
	#									('under_review_prze_approved_lv_2', 'Under Review Aprrove Level 2'), 
	#									('under_review_prze_approved_lv_3', 'Under Review Aprrove Level 3')],
	#				track_visibility='onchange', string= 'Review Status')


	status_history = fields.Text('History', copy=False)


	progress_state = fields.Integer('Progress', default=1)
	amount_in_words = fields.Char('Amount in Words')

	prepared_by_uid = fields.Many2one('res.users', 'Prepared By')
	certified_correct_uid = fields.Many2one('res.users', 'Certified Correct By')
	certified_correct_2_uid = fields.Many2one('res.users', 'Endorsed By')
	under_review_uid = fields.Many2one('res.users', 'Endorsed By')
	for_approval_uid = fields.Many2one('res.users', 'Approval By')

	approve_uid = fields.Many2one('res.users', 'Approved By')
	submitted_uid = fields.Many2one('res.users', 'Submitted By')
	denied_uid = fields.Many2one('res.users', 'Denied By')
	cancelled_uid = fields.Many2one('res.users', 'Cancelled By')

	@api.onchange('purchase_id')
	def purchase_order_change(self):
		#raise Warning(self.purchase_id.analytic_account_id)
		self.analytic_account_id = self.purchase_id.analytic_account_id.id
		res = super(account_invoice_prize_claim,self).purchase_order_change()
		return res

	#New Signatory Workflow for OpEx
	@api.multi
	def action_approve_for_1st_review_opex(self):
	    to_open_invoices = self.filtered(lambda inv: inv.state not in ['draft', 'return'])
	    #To Capture the UI Limitation when Changing State
	    rfp_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
	    if to_open_invoices.filtered(lambda inv: inv.state not in ['draft', 'return']):
	    	
	    	raise Warning(rfp_obj)
	    	if to_open_invoices.filtered(lambda inv: inv.purchase_id):
	    		if to_open_invoices.filtered(lambda inv: inv.purchase_id.state not in ['approved', 'purchase']):
	    			raise UserError(_("Vouchers, Source Document must be approved first in order to validate it."))
	    	elif rfp_obj and rfp_obj.state not in ['approved', 'purchase']:
	    		raise UserError(_("Vouchers Source Document must be approved first in order to validate it."))
	    	else:
	        	raise UserError(_("Voucher must be in draft or return state in order to validate it."))

	    if rfp_obj and rfp_obj.state not in ['approved', 'purchase']:
	    	raise UserError(_("Vouchers Source Document must be approved first in order to validate it."))

	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate an Voucher with a negative total amount."))

	    if self.amount_total < 100000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_below_100k_for_rev1') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    elif self.amount_total < 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_bel_200k_for_rev1') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    elif self.amount_total >= 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_above_200k_for_rev1') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    stats_his = ''
	    stat_rfp_his = ''
	    cert_correct_uid = 0
	    #raise Warning(self.origin)
	    if self.status_history:
	    	stats_his = self.status_history
	    if self.purchase_id:
	    	stat_rfp_his = 'APPROVED RFP :' + '['+ self.purchase_id.write_date +'] ' + self.purchase_id.approve_uid.name + '\n'
	    elif self.origin:
	    	rfp_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
	    	#raise Warning(rfp_obj)
	    	approver_uid_name = ''
	    	if rfp_obj:
	    		if rfp_obj.is_from_rfp:
	    			cert_correct_uid = rfp_obj.approve_uid.id
	    			approver_uid_name = rfp_obj.approve_uid.name
	    		else:
	    			cert_correct_uid = rfp_obj.write_uid.id
	    			approver_uid_name =  rfp_obj.write_uid.name

	    		stat_rfp_his = 'APPROVED RFP :' + '['+ rfp_obj.write_date +'] ' + approver_uid_name + '\n'

	    return self.write({'state': 'under_review', 'certified_correct_uid': cert_correct_uid,  'certified_correct_2_uid': self._uid, 
						   'status_history': 'ENDORSED FOR REVIEW : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stat_rfp_his + stats_his or ''})

	@api.multi
	def action_approve_for_2nd_review_opex(self):
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'under_review')
	    rfp_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
	    if to_open_invoices.filtered(lambda inv: inv.state != 'under_review'):
	    	if to_open_invoices.filtered(lambda inv: inv.purchase_id):
	    		if to_open_invoices.filtered(lambda inv: inv.purchase_id.state not in ['approved', 'purchase']):
	    			raise UserError(_("Vouchers, Source Document must be approved first in order to validate it."))
	    	else:
	        	raise UserError(_("Voucher must be in Under Review state in order to validate it."))

	    if rfp_obj and rfp_obj.state not in ['approved', 'purchase']:
	    	raise UserError(_("Vouchers Source Document must be approved first in order to validate it."))

	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate an Voucher with a negative total amount."))

	    if self.amount_total < 100000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_below_100k_for_rev2') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    elif self.amount_total < 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_bel_200k_for_rev2') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    elif self.amount_total >= 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_above_200k_for_rev2') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    stats_his = ''

	    #raise Warning(self.origin)
	    if self.status_history:
	    	stats_his = self.status_history

	    return self.write({'state': 'under_2nd_review', 'under_review_uid': self._uid, 
						   'status_history': 'ENDORSED FOR 2ND REVIEW : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''})

	@api.multi
	def action_final_approve_opex(self):
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'under_2nd_review')
	    rfp_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
	    if to_open_invoices.filtered(lambda inv: inv.state != 'under_2nd_review'):
	    	if to_open_invoices.filtered(lambda inv: inv.purchase_id):
	    		if to_open_invoices.filtered(lambda inv: inv.purchase_id.state not in ['approved', 'purchase']):
	    			raise UserError(_("Vouchers, Source Document must be approved first in order to validate it."))
	    	else:
	        	raise UserError(_("Voucher must be in Under Final Review state in order to validate it."))

	    if rfp_obj and rfp_obj.state not in ['approved', 'purchase']:
	    	raise UserError(_("Vouchers Source Document must be approved first in order to validate it."))

	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate an Voucher with a negative total amount."))

	    if self.amount_total < 100000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_below_100k_approved') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    elif self.amount_total < 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_bel_200k_approved') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    elif self.amount_total >= 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.opex_group_allow_to_approve_above_200k_approved') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Voucher."))
	    stats_his = ''

	    #raise Warning(self.origin)
	    if self.status_history:
	    	stats_his = self.status_history

	    res = self.write({'state': 'approved', 'approved_uid': self._uid, 
						   'status_history': 'APPROVED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''})

	    if res:
	    	self.action_invoice_open()

	#New Signatory Workflow for Charity
	@api.multi
	def action_to_submit_charity_claim(self):
	    to_open_invoices = self.filtered(lambda inv: inv.state not in ['draft', 'return'])
	    if to_open_invoices.filtered(lambda inv: inv.state not in ['draft', 'return']):
	        raise UserError(_("Prize Claim must be in draft state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))

	    stats_his = ''
	    if self.status_history:
	    	stats_his = self.status_history
	    state_dict ={'state': 'submit', 'submitted_uid': self._uid,
	    	 'status_history': 'SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''}
	    if self.state == 'draft':
	    	state_dict['status_history'] = 'SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''
	    elif self.state == 'return':
	    	state_dict['status_history'] = 'RE-SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''
	    return self.write(state_dict)	

	@api.multi
	def action_to_approve_for_1st_review_charity_claim(self):	
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'submit')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'submit'):
	        raise UserError(_("Prize Claim must be in Submitted state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))
	    if self.amount_total < 100000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_below_100k_for_rev1') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    elif self.amount_total >= 100000.00 and self.amount_total < 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_above_100k_bel_200k_for_rev1') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    elif self.amount_total >= 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_above_200k_for_rev1') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    stats_his = ''
	    if self.status_history:
	    	stats_his = self.status_history
	    return self.write({'state': 'under_review', 'certified_correct_uid': self._uid, 
						   'status_history': 'ENDORSED FOR 1ST REVIEW : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''})


	@api.multi
	def action_to_approve_for_2nd_review_charity_claim(self):	
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'under_review')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'under_review'):
	        raise UserError(_("Prize Claim must be in Under Review state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))
	    if self.amount_total < 100000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_below_100k_for_rev2') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    elif self.amount_total >= 100000.00 and self.amount_total < 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_above_100k_bel_200k_for_rev2') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    elif self.amount_total >= 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_above_200k_for_rev2') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    stats_his = ''
	    if self.status_history:
	    	stats_his = self.status_history
	    return self.write({'state': 'under_2nd_review', 'certified_correct_2_uid': self._uid, 
						   'status_history': 'ENDORSED FOR 2ND REVIEW : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''})

	@api.multi
	def action_to_approve_for_approval_charity_claim(self):
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'under_2nd_review')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'under_2nd_review'):
	        raise UserError(_("Prize Claim must be in 2nd Review state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))
	    if self.amount_total < 100000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_below_100k_for_approval') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    elif self.amount_total >= 100000.00 and self.amount_total < 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_above_100k_bel_200k_for_approval') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    elif self.amount_total >= 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_above_200k_for_approval') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    stats_his = ''
	    if self.status_history:
	    	stats_his = self.status_history
	    return self.write({'state': 'for_approval', 'for_approval_uid': self._uid, 
						   'status_history': 'ENDORSED FOR APPROVAL : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''})

	@api.multi
	def action_final_approve_charity_claim(self):
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'for_approval')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'for_approval'):
	        raise UserError(_("Prize Claim must be in For Approval state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))
	    if self.amount_total < 100000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_below_100k_approved') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    elif self.amount_total >= 100000.00 and self.amount_total < 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_above_100k_bel_200k_approved') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    elif self.amount_total >= 200000.00:
	    	if self.env.ref('account_prize_claim_pcso.ccf_group_allow_to_approve_above_200k_approved') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim."))
	    stats_his = ''
	    if self.status_history:
	    	stats_his = self.status_history
	    res = self.write({'state': 'approved', 'approve_uid': self._uid, 
						   'status_history': 'APPROVED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''})

	    if res:
	    	self.action_invoice_open()




	#New Signatory Workflow for Prize Claim
	@api.multi
	def action_to_submit_prize_claim(self):
	    to_open_invoices = self.filtered(lambda inv: inv.state not in ['draft', 'return'])
	    if to_open_invoices.filtered(lambda inv: inv.state not in ['draft', 'return']):
	        raise UserError(_("Prize Claim must be in draft state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))


	    if self.jackpot_prize == True:
	    	if self.env.ref('account_prize_claim_pcso.pcf_group_allow_submit_jackpot') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to submit the Claim. Prize Claim is a Jackpot Prize."))
	    stats_his = ''
	    if self.status_history:
	    	stats_his = self.status_history
	    state_dict ={'state': 'submit', 'submitted_uid': self._uid,
	    	 'status_history': 'SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''}
	    if self.state == 'draft':
	    	state_dict['status_history'] = 'SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''
	    elif self.state == 'return':
	    	state_dict['status_history'] = 'RE-SUBMITTED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''
	    return self.write(state_dict)


	@api.multi
	def action_to_approve_for_review_prize_claim(self):	
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'submit')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'submit'):
	        raise UserError(_("Prize Claim must be in Submitted state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))
	    if self.jackpot_prize == True:
	    	if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_jackpot_rev') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Approved the Claim. Prize Claim is a Jackpot Prize."))
	    else:
	    	if self.amount_total < 100000.00:
	    		if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_non_jack_below_100k_rev') not in self.env.user.groups_id:
	    			raise UserError(_("User has no rights to Approved the Claim."))
	    	elif self.amount_total >= 100000.00:
	    		if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_non_jack_above_100k_rev') not in self.env.user.groups_id:
	    			raise UserError(_("User has no rights to Approved the Claim."))
	    stats_his = ''
	    if self.status_history:
	    	stats_his = self.status_history

	    return self.write({'state': 'under_review', 'certified_correct_uid': self._uid, 
	    				   'status_history': 'ENDORSED FOR REVIEW : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + stats_his or ''})


	@api.multi
	def action_to_approve_for_approval_prize_claim(self):	
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'under_review')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'under_review'):
	        raise UserError(_("Prize Claim must be in Under Review state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))
	    if self.jackpot_prize == True:
	    	if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_jackpot_for_approv') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Endorse the Claim. Prize Claim is a Jackpot Prize."))
	    else:
	    	if self.amount_total < 100000.00:
	    		if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_non_jack_below_100k_for_approv') not in self.env.user.groups_id:
	    			raise UserError(_("User has no rights to Endorse the Claim."))
	    	elif self.amount_total >= 100000.00:
	    		if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_non_jack_above_100k_for_approv') not in self.env.user.groups_id:
	    			raise UserError(_("User has no rights to Endorse the Claim."))
	    return self.write({'state': 'for_approval', 'for_approval_uid': self._uid,
	    				  'status_history': 'ENDORSED FOR APPROVAL : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + self.status_history or ''})

	@api.multi
	def action_final_approve(self):	
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'for_approval')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'for_approval'):
	        raise UserError(_("Prize Claim must be in For Approval state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount."))
	    if self.jackpot_prize == True:
	    	if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_jackpot_approved') not in self.env.user.groups_id:
	    		raise UserError(_("User has no rights to Endorse the Claim. Prize Claim is a Jackpot Prize."))
	    else:
	    	if self.amount_total < 100000.00:
	    		if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_non_jack_below_100k_approved') not in self.env.user.groups_id:
	    			raise UserError(_("User has no rights to Endorse the Claim."))
	    	elif self.amount_total >= 100000.00:
	    		if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve_non_jack_above_100k_approved') not in self.env.user.groups_id:
	    			raise UserError(_("User has no rights to Endorse the Claim."))
	    res = self.write({'state': 'approved', 'approve_uid': self._uid,
	    				  'status_history': 'APPROVED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n' + self.status_history or ''})
	    if res:
	    	self.action_invoice_open()

	@api.multi
	def action_set_to_return(self, reason):

	    stats_his =''
	    if self.status_history:
	    	stats_his = self.status_history
	    return self.write({'state': 'return', 'denied_uid': self._uid,
	    				  'status_history': 'RETURNED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n *****REASON \n' + reason  + '\n' + stats_his})
	@api.multi
	def action_set_to_cancel(self, reason=''):
	    stats_his =''
	    if self.status_history:
	    	stats_his = self.status_history
	    return self.write({'state': 'cancel', 'cancelled_uid': self._uid,
	    				  'status_history': 'CANCELLED : ' + '['+ self.write_date +'] ' + self.env.user.name + '\n *****REASON \n' + reason  + '\n' + stats_his + reason + '\n'})	
	    				  	
	@api.onchange('amount_total')
	def _onchange_amount_total(self):
		if hasattr(super(account_invoice_prize_claim, self), '_onchange_amount'):
			super(account_invoice_prize_claim, self)._onchange_amount()
		self.amount_in_words =  self.env['account.payment']._get_check_amount_in_words(self.amount_total) #self.currency_id.amount_to_text(self.amount_total)

	@api.multi
	def get_amount_in_words(self):
		self.ensure_one()
		return  self.env['account.payment']._get_check_amount_in_words(self.amount_total).upper() + ' ONLY'  #self.currency_id.amount_to_text(self.amount_total).upper() + ' ONLY'


	@api.multi
	def get_prepared_by_rfp(self):
		self.ensure_one
		if self.origin:
			rfp_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
			return rfp_obj.create_uid.name
		return False

	@api.multi
	def get_certified_by_rfp(self):
		self.ensure_one
		if self.origin:
			rfp_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
			return rfp_obj.submitted_uid.name
		return False


	@api.multi
	def get_certified_by_sig_rfp(self):
		self.ensure_one
		if self.origin:
			rfp_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
			obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', rfp_obj.submitted_uid.id)])
			if obj_employee:
				return obj_employee.image_signature
		return False

	@api.multi
	def get_prepared_by_sig_rfp(self):
		self.ensure_one
		if self.origin:
			rfp_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
			obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', rfp_obj.create_uid.id)])
			if obj_employee:
				return obj_employee.image_signature
		return False

	@api.multi
	def get_prepared_by(self):
		self.ensure_one
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.prepared_by_uid.id or False)])

		if obj_employee:
			return obj_employee.name
		else:
			return self.prepared_by_uid.name

	@api.multi
	def get_certified_by(self):
		self.ensure_one
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.submitted_uid.id or False)])

		if obj_employee:
			return obj_employee.name
		else:
			return self.submitted_uid.name

	@api.multi
	def get_certified_under_box_A_by(self):
		self.ensure_one
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.certified_correct_uid.id or False)])

		if obj_employee:
			return obj_employee.name
		else:
			return self.submitted_uid.name

	@api.multi
	def get_certified_under_box_B_by(self):
		self.ensure_one
		ret_id = False
		if self.transaction_type  == 'prize_claim':
			ret_id = self.for_approval_uid.id
		elif self.transaction_type  == 'charity':
			ret_id = self.for_approval_uid.id
		else:
			ret_id = self.under_review_uid.id

		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', ret_id)])

		if obj_employee:
			return obj_employee.name
		else:
			return self.submitted_uid.name


	@api.multi
	def get_certified_under_box_B_jl_by(self):
		self.ensure_one
		ret_id=False
		if self.transaction_type  == 'prize_claim':
			ret_id = self.submitted_uid.id
		elif self.transaction_type  == 'charity':
			ret_id = self.certified_correct_2_uid.id
		else:
			ret_id = self.certified_correct_2_uid.id

		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', ret_id)])

		if obj_employee:
			return obj_employee.name
		else:
			return False			

	@api.multi
	def get_certified_under_box_C_by(self):
		self.ensure_one
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.approve_uid.id or False)])

		if obj_employee:
			return obj_employee.name
		else:
			return self.approve_uid.name


	@api.multi
	def get_approver_signatory_under_box_A(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.certified_correct_uid.id or False)])
		if obj_employee:
			return obj_employee.image_signature
		else:
			return False

	@api.multi
	def get_approver_signatory_under_box_B(self):
		self.ensure_one()
		ret_id = False
		if self.transaction_type  == 'prize_claim':
			ret_id = self.for_approval_uid.id
		elif self.transaction_type  == 'charity':
			ret_id = self.for_approval_uid.id
		else:
			ret_id = self.under_review_uid.id		
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', ret_id)])
		if obj_employee:
			return obj_employee.image_signature
		else:
			return False

	@api.multi
	def get_approver_signatory_under_box_B_jl_by(self):
		self.ensure_one()
		ret_id = False
		if self.transaction_type  == 'prize_claim':
			ret_id = self.for_approval_uid.id
		elif self.transaction_type  == 'charity':
			ret_id = self.for_approval_uid.id
		else:
			ret_id = self.under_review_uid.id		
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', ret_id)])
		if obj_employee:
			return obj_employee.image_signature
		else:
			return False


	@api.multi
	def get_approver_signatory_under_box_C(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.approve_uid.id or False)])
		if obj_employee:
			return obj_employee.image_signature
		else:
			return False


	@api.multi
	def get_approver_name(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.approve_uid.id or False)])
		if obj_employee:
			return obj_employee.name
		else:
			return self.approve_uid.name



	@api.multi
	def get_approver_acc_dig_sig(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.for_approval_uid.id or False)])
		if obj_employee:
			return obj_employee.image_signature
		else:
			return False

	@api.multi
	def get_approver_dig_sig(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.approve_uid.id or False)])
		if obj_employee:
			return obj_employee.image_signature
		else:
			return False

	@api.multi
	def get_submitter_dig_sig(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.certified_correct_uid.id or False)])
		if obj_employee:
			return obj_employee.image_signature
		else:
			return False

	@api.multi
	def get_submitter_name(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.certified_correct_uid.id or False)])
		if obj_employee:
			return obj_employee.name
		else:
			return self.submitted_uid.name

	@api.multi
	def get_submitter_position(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.certified_correct_uid.id or False)])
		if obj_employee:
			return obj_employee.job_id.name
		else:
			return False

	@api.multi
	def get_date_in_words(self):
		self.ensure_one()
		new_formatted_date = datetime.strptime(self.transaction_date, '%Y-%m-%d')
		return new_formatted_date.strftime('%B %d,%Y')



	#OBSELETE
	#@api.multi
	#def action_to_submit_prize_claim(self):
	    # lots of duplicate calls to action_invoice_open, so we remove those already open
	#    to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
	#    if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
	#        raise UserError(_("Prize Claim must be in draft state in order to validate it."))
	#    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	#        raise UserError(_("You cannot validate a Prize Claim with a negative total amount. You should create a credit note instead."))
	#    if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_submit') in self.env.user.groups_id and self.jackpot_prize:
	#    	raise UserError(_("User has no rights to submit the Claim. Prize Claim is a Jackpot Prize."))
	#    return to_open_invoices.invoice_validate_submit()

	@api.model
	def create(self, vals):
		if vals.get('draft_number_sequence', _('New Voucher')) == _('New Voucher'):
			seq_str = ''
			if self._context.get('transaction_type') == 'prize_claim':
				seq_str = 'PRF' + self.env['ir.sequence'].next_by_code('account.invoice.voucher.seq') 
			elif self._context.get('transaction_type')== 'charity':
				seq_str = 'CHF' + self.env['ir.sequence'].next_by_code('account.invoice.voucher.seq') 
			else:
				seq_str = 'OPX' + self.env['ir.sequence'].next_by_code('account.invoice.voucher.seq') 

			vals['draft_number_sequence'] = seq_str
		
		if vals.get('jackpot_prize'):
			if self.env.ref('account_prize_claim_pcso.pcf_group_allow_create_jackpot') not in self.env.user.groups_id:
				raise UserError(_("User has no access to Create the Claim. Prize Claim is a Jackpot Prize."))
		res = super(account_invoice_prize_claim, self).create(vals)

		return res

	#@api.one
	#def action_to_submit_prize_claim_jackpot(self):
	    # lots of duplicate calls to action_invoice_open, so we remove those already open
	#    to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
	#    if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
	#        raise UserError(_("Prize Claim must be in draft state in order to validate it."))
	#    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	#        raise UserError(_("You cannot validate a Prize Claim with a negative total amount. You should create a credit note instead."))
	#    if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_submit') in self.env.user.groups_id and self.amount_total >=1000000.00:
	 #   	raise UserError(_("User has no rights to submit the Claim. Prize Claim is a Jackpot Prize."))
	#    return to_open_invoices.invoice_validate_submit()

	@api.multi
	def action_to_approved_prize_claim(self):
	    # lots of duplicate calls to action_invoice_open, so we remove those already open
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'submit')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'submit'):
	        raise UserError(_("Invoice must be in submit state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
	    if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve') in self.env.user.groups_id and self.jackpot_prize:
	    	raise UserError(_("User has no rights to Approve the Claim. Prize Claim is a Jackpot Prize."))

	    #to_open_invoices.action_date_assign()
	    #to_open_invoices.action_move_create()

	    #for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
	    #    invoice.message_subscribe([invoice.partner_id.id])
	    #self._check_duplicate_supplier_reference()
	    return self.write({'state': 'approved', 'approve_uid': self._uid})

	@api.multi
	def action_to_appoved_prize_claim_jackpot(self):
		for claim in self:
			claim.action_to_appoved_prize_claim()

	@api.multi
	def action_to_denied_prize_claim(self):
	    # lots of duplicate calls to action_invoice_open, so we remove those already open
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'submit')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'submit'):
	        raise UserError(_("Invoice must be in submit state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
	    for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
	        invoice.message_subscribe([invoice.partner_id.id])
	    if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve') in self.env.user.groups_id and to_open_invoices.filtered(lambda inv: inv.transaction_type == 'prize_claim'):	    
	    	raise UserError(_("User has no rights to Deny the Claim. Prize Claim is a Jackpot Prize."))
	    #self._check_duplicate_supplier_reference()
	    return self.write({'state': 'denied', 'denied_uid': self._uid})

	@api.multi
	def action_to_denied_prize_claim_jackpot(self):
		self.action_to_denied_prize_claim()

	@api.multi
	def invoice_validate_submit(self):
	    for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
	        invoice.message_subscribe([invoice.partner_id.id])
	    #self._check_duplicate_supplier_reference()
	    return self.write({'state': 'submit', 'submitted_uid': self._uid})

	@api.multi
	def action_invoice_open(self):
	    # lots of duplicate calls to action_invoice_open, so we remove those already open
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'approved') and to_open_invoices.filtered(lambda inv: inv.transaction_type == False):
	    	#if to_open_invoices.filtered(lambda inv: inv.state != 'draft')
	        raise UserError(_("Invoice must be in submit state in order to validate it."))
	    #if to_open_invoices.filtered(lambda inv: inv.state != 'approved') and to_open_invoices.filtered(lambda inv: inv.transaction_type != False):
	    #    raise UserError(_("Price Claim must be in approved state in order to validate it."))	       
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
	    to_open_invoices.action_date_assign()
	    to_open_invoices.action_move_create()
	    return to_open_invoices.invoice_validate()

	@api.multi
	def action_invoce_open_jackpot(self):
		self.action_invoice_open()

	@api.multi
	def invoice_validate(self):
		res = super(account_invoice_prize_claim, self).invoice_validate()
		return self.write({'approve_uid': self._uid})

	def _prepare_invoice_line_from_po_line(self, line):
	    if line.product_id.purchase_method == 'purchase':
	        qty = line.product_qty - line.qty_invoiced
	    else:
	        qty = line.qty_received - line.qty_invoiced

	    if line.order_id.is_from_rfp == True:
	    	qty = 1
	    	
	    if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
	        qty = 0.0
	    taxes = line.taxes_id
	    invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
	    invoice_line = self.env['account.invoice.line']
	    data = {
	        'purchase_line_id': line.id,
	        'name': line.order_id.name+': '+line.name,
	        'origin': line.order_id.origin,
	        'uom_id': line.product_uom.id,
	        'product_id': line.product_id.id,
	        'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
	        'price_unit': line.order_id.currency_id.with_context(date=self.date_invoice).compute(line.price_unit, self.currency_id, round=False),
	        'quantity': qty,
	        'discount': 0.0,
	        'account_analytic_id': line.account_analytic_id.id,
	        'analytic_tag_ids': line.analytic_tag_ids.ids,
	        'invoice_line_tax_ids': invoice_line_tax_ids.ids
	    }
	    account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.order_id.fiscal_position_id, self.env.user.company_id)
	    if account:
	        data['account_id'] = account.id
	    return data


	@api.multi
	def name_get(self):
		TYPES = {
			'out_invoice': _('Invoice'),
			'in_invoice': _('Vendor Bill'),
			'out_refund': _('Credit Note'),
			'in_refund': _('Vendor Credit note'),
		}
		result = []
		for inv in self:
			if inv.transaction_type == 'prize_claim':
				result.append((inv.id, "%s %s" % (inv.number or'Prize Claim', inv.name or '')))
			elif inv.transaction_type == 'charity':
				result.append((inv.id, "%s %s" % (inv.number or'Charity Claim', inv.name or '')))
			else:
				result.append((inv.id, "%s %s" % (inv.number or TYPES[inv.type], inv.name or '')))
		return result
