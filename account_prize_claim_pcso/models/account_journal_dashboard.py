import json
from datetime import datetime, timedelta

from babel.dates import format_datetime, format_date

from odoo import models, api, _, fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang
_logger = logging.getLogger(__name__)


class account_journal_dashboard(models.Model):
    _inherit = "account.journal"


    @api.multi
    def open_action(self):
    	raise Warning(111)
    	action = super(account_journal_dashboard, self).open_action()
    	#action_name = self._context.get('action_name', False)
    	raise Warning(action)
    	return action
    	#if not action_name:
    	#	action = super(account_journal, self).open_action()
    	#	raise Warning(action)
    	#	return action
