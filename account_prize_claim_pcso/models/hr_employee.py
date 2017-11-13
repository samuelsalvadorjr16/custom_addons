# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


_logger = logging.getLogger(__name__)

class hr_employee(models.Model):
	_inherit = ["hr.employee"]

	# image: all image fields are base64 encoded and PIL-supported
	image_signature = fields.Binary("Digitized Signed", attachment=True,
	    									help="This field holds the image used as Digitized Signature, limited to 1024x1024px.")
	#image_signature_medium = fields.Binary("Medium-sized photo", attachment=True,
	#									    help="Medium-sized Digitized Signature photo of the employee. It is automatically "
	#									         "resized as a 128x128px image, with aspect ratio preserved. ")
	#image_signature_small = fields.Binary("Small-sized photo", attachment=True,
	#								    help="Small-sized Digitized Signature photo of the employee. It is automatically "
	#								         "resized as a 64x64px image, with aspect ratio preserved. "
	#								         "Use this field anywhere a small image is required.")

class hr_department(models.Model):
	_inherit = 'hr.department'
	account_analytic_id = fields.Many2one('account.analytic.account', string='Cost Center/Anaytic Account')