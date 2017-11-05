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

class res_user(models.Model):
	_inherit = 'res.users'

	employee_ids = fields.One2many('hr.employee', 'user_id', string='Employee')
	department_id = fields.Many2one('hr.department', related='employee_ids.department_id', string="Department")
	job_id = fields.Many2one('hr.job', related='employee_ids.job_id', string="Department")
#class 