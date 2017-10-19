# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_invoice_prize_claim(models.Model):
	_inherit = ["account.invoice"]

	partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
	    required=True, readonly=True, states={'draft': [('readonly', False)]},
	    track_visibility='always')

	branch_id = fields.Many2one('config.prize.branch', string='Branch')
	transaction_id = fields.Many2one('config.prize.transactiontype', string='Transaction Type')

	claimant_id = fields.Many2one('res.partner', string='Claimant')
	claimant_type_id = fields.Selection(related='partner_id.id_type', string='ID Type')
	claimant_id_number = fields.Char(related='partner_id.id_number', string='ID Number', store=True)
	claimant_gender = fields.Selection(related='partner_id.gender', string='Gender', store=True)
	claimant_occupation = fields.Char( related='partner_id.function', string='Occupation', store=True)
	claimant_birthdate = fields.Date( related='partner_id.birthdate', string='Birthday', store=True)
	remarks = fields.Text('Remarks')
	transaction_date = fields.Date('Transaction Date')

	transaction_type = fields.Selection([
	        ('prize_claim','Prize Claim'),
	        ('charity','Charity Fund'),
	    ], index=True, change_default=True,string='Transaction Type')

	type = fields.Selection([
	        ('out_invoice','Customer Invoice'),
	        ('in_invoice','Vendor Bill'),
	        ('out_refund','Customer Credit Note'),
	        ('in_refund','Vendor Credit Note'),
	        ('in_prizeclaim_invoice','Prize Claim'),
	        ('in_charityfund_invoice','Charity Fund'),
	    ], readonly=True, index=True, change_default=True,
	    default=lambda self: self._context.get('type', 'out_invoice'),
	    track_visibility='always')

	state = fields.Selection([
	        ('draft','Draft'),
	        ('open', 'Open'),
	        ('paid', 'Paid'),
	        ('cancel', 'Cancelled'),
	        ('submit', 'Submitted'),
	        ('approved', 'Approved'),
	        ('denied', 'Denied'),
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

class account_invoice_line_prize_claim(models.Model):
	_inherit = ["account.invoice.line"]

	draw_id = fields.Many2one2('config.prize.draws', 'Draw ID')
	draw_date = fields.Date('config.prize.draws',related='draw_id.draw_date', string='Draw Date')
	draw_result = fields.Char('config.prize.draws',related='draw_id.draw_result', string='Draw Date')
	draw_gametype = fields.Many2one('config.prize.draws',related='draw_id.gametype_id.id', string='Game Type')
	bettype_id = fields.Many2one('config.prize.bettype', 'Bet Type')
	agency_id = fields.Many2one('config.prize.agency', 'Agency')
	ticket_serial = fields.Char('Ticket Serial')
	first_prize = fields.Float(string='First Prize', digits=dp.get_precision('Price Claim First Prize'))
	second_prize = fields.Float(string='Second Prize', digits=dp.get_precision('Price Claim Second Prize'))
	third_prize = fields.Float(string='Third Prize', digits=dp.get_precision('Price Claim Third Prize'))
	fourth_prize = fields.Float(string='Fourth Prize', digits=dp.get_precision('Price Claim Fourth Prize'))
	fifth_prize = fields.Float(string='Fifth Prize', digits=dp.get_precision('Price Claim Fifth Prize'))
	prize_amount = fields.Float(string='Prize Amount')
	#Override Fields
	name = fields.Text(string='Description')
	price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
