# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.modules.module import get_module_resource

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_journal(models.Model):
	_inherit = ["account.journal"]

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