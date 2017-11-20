# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class pcso_transaction(models.Model):
	_inherit = ["pcso.transaction"]

	_sql_constraints=[('pcso_transaction_name_uniq',
						'UNIQUE (name)',
						'GL Number Already Exists')]

