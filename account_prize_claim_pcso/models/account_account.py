# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_account(models.Model):
	_inherit = ["account.account"]

	object_code_id = fields.Many2one('account.account', string='Cost Object Code')
	prior_year_acctcode_id = fields.Many2one('account.account', string='Prior Year Account')

class account_tax(models.Model):
	_inherit=["account.tax"]

	tax_type = fields.Selection([
            ('goods','Goods'),
            ('service','Service'),
            ], string ="Tax Type",
            default='service')	