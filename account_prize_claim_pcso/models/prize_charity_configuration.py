# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


_logger = logging.getLogger(__name__)

class prize_config_branch(models.Model):
	_name = 'config.prize.branch'
	
	name = fields.Char('Name')

class prize_config_transaction_type(models.Model):
	_name = 'config.prize.transactiontype'

	name = fields.Char('Name')

class prize_config_agency(models.Model):
	_name = "config.prize.agency"

	name = fields.Char('Name')
	agency_id = fields.Char('ID')
	owner_id = fields.Many2one('res.partner', 'Owner')

class prize_config_gametype(models.Model):
	_name = 'config.prize.gametype'

	name = fields.Char('Name')
	id_char = fields.Char('ID')

class prize_config_bettype(models.Model):
	_name = 'config.prize.bettype'

	name = fields.Char('Name')
	id_char = fields.Char('ID')

class prize_config_draws(models.Model):
	_name = "config.prize.draws"
	_rec_name='drawid'

	drawid = fields.Char('Draw ID')
	draw_date = fields.Datetime('Draw Date')
	draw_result = fields.Char('Draw Result')
	gametype_id = fields.Many2one('config.prize.gametype', 'Game Type')