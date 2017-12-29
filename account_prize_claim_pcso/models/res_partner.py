# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class res_partner(models.Model):
	_inherit = "res.partner"

	tax_ids = fields.Many2many(
			'account.tax',
			'account_partner_tax_rel', 'res_partner_id', 'tax_id',
			string='Taxes', 
			domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)],
			)