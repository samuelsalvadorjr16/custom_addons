import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.modules.module import get_module_resource

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_journal(models.Model):
	_inherit = "account.journal"

	type = fields.Selection([
	        ('sale', 'Sale'),
	        ('purchase', 'Purchase'),
	        ('cash', 'Cash'),
	        ('bank', 'Bank'),
	        ('prize_fund', 'Prize Fund'),
	        ('charity_fund', 'Charity Fund'),	        
	        ('general', 'Miscellaneous'),
	    ], required=True,
	    help="Select 'Sale' for customer invoices journals.\n"\
	    "Select 'Purchase' for vendor bills journals.\n"\
	    "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n"\
	    "Select 'Prize Fund' for journals that are used in Prize Claims.\n"\
	    "Select 'Charity Fund' for journals that are Charity Claims.\n"\
	    "Select 'General' for miscellaneous operations journals.")

	@api.multi
	def open_action(self):
		action_name = self._context.get('action_name', False)
		if self.name == 'Prize Fund':
			[action] = self.env.ref('account_prize_claim_pcso.action_invoice_prize_claim').read()
		elif self.name == 'Charity Fund':
			[action] = self.env.ref('account_prize_claim_pcso.action_invoice_charity_claim').read()
		else:
			action = super(account_journal, self).open_action()

		return action

	@api.multi
	def action_create_new(self):
		ctx = self._context.copy()
		model = 'account.invoice'
		if self.type == 'sale':
		    ctx.update({'journal_type': self.type, 'default_type': 'out_invoice', 'type': 'out_invoice', 'default_journal_id': self.id})
		    if ctx.get('refund'):
		        ctx.update({'default_type':'out_refund', 'type':'out_refund'})
		    view_id = self.env.ref('account.invoice_form').id
		elif self.type == 'purchase':
			
			if self.name == 'Prize Fund':

				ctx.update({'default_type': 'in_invoice', 
							'type': 'in_invoice', 
							'journal_type': self.type, 
							'default_transaction_type': 'prize_claim', 
							'transaction_type': 'prize_claim', 
							'default_journal_id': 7})
				view_id = self.env.ref('account_prize_claim_pcso.invoice_prize_claim_form').id
			elif self.name == 'Charity Fund':

				ctx.update({'default_type': 'in_invoice', 
							'type': 'in_invoice', 
							'journal_type': self.type, 
							'default_transaction_type': 'charity', 
							'transaction_type': 'charity', 
							'default_journal_id': 8})
				view_id = self.env.ref('account_prize_claim_pcso.invoice_charity_claim_form').id				
			else:
			    ctx.update({'journal_type': self.type, 'default_type': 'in_invoice', 'type': 'in_invoice', 'default_journal_id': self.id})
			    if ctx.get('refund'):
			        ctx.update({'default_type': 'in_refund', 'type': 'in_refund'})
			    view_id = self.env.ref('account.invoice_supplier_form').id
		else:
		    ctx.update({'default_journal_id': self.id})
		    view_id = self.env.ref('account.view_move_form').id
		    model = 'account.move'
		return {
		    'name': _('Create invoice/bill'),
		    'type': 'ir.actions.act_window',
		    'view_type': 'form',
		    'view_mode': 'form',
		    'res_model': model,
		    'view_id': view_id,
		    'context': ctx,
		}