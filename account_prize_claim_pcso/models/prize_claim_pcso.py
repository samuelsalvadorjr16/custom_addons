# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
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
	transaction_id = fields.Many2one('config.prize.transactiontype', string='Transaction Type')

	claimant_id = fields.Many2one('res.partner', string='Claimant')
	claimant_type_id = fields.Selection(related='partner_id.id_type', string='ID Type')
	claimant_id_number = fields.Char(related='partner_id.id_number', string='ID Number', store=True)
	claimant_gender = fields.Selection(related='partner_id.gender', string='Gender', store=True)
	claimant_occupation = fields.Char( related='partner_id.function', string='Occupation', store=True)
	claimant_birthdate = fields.Date( related='partner_id.birthdate', string='Birthday', store=True)
	remarks = fields.Text('Remarks')
	transaction_date = fields.Date('Transaction Date', default=fields.Date.context_today)
	jackpot_prize = fields.Boolean('Jackpot Winner', readonly=True, states={'draft': [('readonly', False)]})

	transaction_type = fields.Selection([
	        ('prize_claim','Prize Claim'),
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
	        ('submit', 'Submitted'),
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


	amount_in_words = fields.Char('Amount in Words')

	approve_uid = fields.Many2one('res.users', 'Approved By')
	submitted_uid = fields.Many2one('res.users', 'Submitted By')
	denied_uid = fields.Many2one('res.users', 'Denied By')

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
	def get_approver_name(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.approve_uid.id or False)])
		if obj_employee:
			return obj_employee.name
		else:
			return self.approve_uid.name

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
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.submitted_uid.id or False)])
		if obj_employee:
			return obj_employee.image_signature
		else:
			return False

	@api.multi
	def get_submitter_name(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.submitted_uid.id or False)])
		if obj_employee:
			return obj_employee.name
		else:
			return self.submitted_uid.name

	@api.multi
	def get_submitter_position(self):
		self.ensure_one()
		obj_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.submitted_uid.id or False)])
		if obj_employee:
			return obj_employee.job_id.name
		else:
			return False

	@api.multi
	def get_date_in_words(self):
		self.ensure_one()
		new_formatted_date = datetime.strptime(self.transaction_date, '%Y-%m-%d')
		return new_formatted_date.strftime('%B %d,%Y')




	@api.multi
	def action_to_submit_prize_claim(self):
	    # lots of duplicate calls to action_invoice_open, so we remove those already open
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
	        raise UserError(_("Prize Claim must be in draft state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount. You should create a credit note instead."))
	    if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_submit') in self.env.user.groups_id and self.amount_total >=1000000.00:
	    	raise UserError(_("User has no rights to submit the Claim. Prize Claim is a Jackpot Prize."))
	    return to_open_invoices.invoice_validate_submit()

	@api.one
	def action_to_submit_prize_claim_jackpot(self):
	    # lots of duplicate calls to action_invoice_open, so we remove those already open
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
	        raise UserError(_("Prize Claim must be in draft state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate a Prize Claim with a negative total amount. You should create a credit note instead."))
	    if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_submit') in self.env.user.groups_id and self.amount_total >=1000000.00:
	    	raise UserError(_("User has no rights to submit the Claim. Prize Claim is a Jackpot Prize."))
	    return to_open_invoices.invoice_validate_submit()

	@api.multi
	def action_to_approved_prize_claim(self):
	    # lots of duplicate calls to action_invoice_open, so we remove those already open
	    to_open_invoices = self.filtered(lambda inv: inv.state != 'submit')
	    if to_open_invoices.filtered(lambda inv: inv.state != 'submit'):
	        raise UserError(_("Invoice must be in submit state in order to validate it."))
	    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
	        raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
	    if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve') in self.env.user.groups_id and self.amount_total >=1000000.00:
	    	raise UserError(_("User has no rights to Approve the Claim. Prize Claim is a Jackpot Prize."))
		#if  self.env.ref('primer_extend_security_access.pcf_group_allow_to_approve') in self.env.user.groups_id and self.amount_total >=1000000.00:
		#	raise UserError(_("User has no rights to Approve the Claim. Prize Claim is a Jackpot Prize."))

	    to_open_invoices.action_date_assign()
	    to_open_invoices.action_move_create()

	    for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
	        invoice.message_subscribe([invoice.partner_id.id])
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
	    if self.env.ref('account_prize_claim_pcso.pcf_group_allow_to_approve') in self.env.user.groups_id and to_open_invoices.filtered(lambda inv: inv.transaction_type == 'prize_claim'):# and self.amount_total >=1000000.00:
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
	    if to_open_invoices.filtered(lambda inv: inv.state != 'submit') and to_open_invoices.filtered(lambda inv: inv.transaction_type == False):
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
