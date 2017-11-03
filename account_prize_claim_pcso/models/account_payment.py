# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.modules.module import get_module_resource

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_payment(models.Model):
	_inherit = "account.payment"

	#This will mark in Charity/ Prize Claim for the Designation of Different Documents for Payment
	pcso_transaction_type = fields.Selection([
	        ('prize_claim','Prize Fund'),
	        ('charity','Charity Fund'),
	    ], index=True, change_default=True,string='PCSO Transaction Type')