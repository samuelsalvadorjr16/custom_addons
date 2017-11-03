# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)

class mail_tracking_value(models.Model):
	_inherit = 'mail.tracking.value'

	@api.model
	def create_tracking_values(self, initial_value, new_value, col_name, col_info):
		values  =super(mail_tracking_value, self).create_tracking_values(initial_value, new_value, col_name, col_info)
		_logger.info(self.mail_message_id.res_id)
		_logger.info(values)		
		#raise Warning(values)
		return values

	@api.model
	def create(self, values):
		_logger.info('---------------------------------------------------------------------------->>>')
		_logger.info(values['mail_message_id'])
		res_id  =super(mail_tracking_value, self).create(values)

		#Update the TYPE for the following
		if res_id:
			if res_id.mail_message_id.model =='account.invoice':
				type_name =''
				if res_id.mail_message_id.record_name == 'Prize Claim ':
					type_name = 'Prize Claim'
				elif res_id.mail_message_id.record_name == 'Charity Claim ':
					type_name = 'Charity Claim'
				else:
					type_name = 'Opex Voucher'
				#raise Warning(res_id.mail_message_id.record_name)
				obj_mail_tracking_value = self.env['mail.tracking.value'].search([('mail_message_id', '=', res_id.mail_message_id.id), ('field', '=', 'type')])
				obj_mail_tracking_value.write({'old_value_char': obj_mail_tracking_value.new_value_char, 'new_value_char': type_name})
				obj_mail_tracking_value = self.env['mail.tracking.value'].search([('mail_message_id', '=', res_id.mail_message_id.id), ('field', '=', 'write_date')])
				obj_mail_tracking_value.write({'field_desc': 'Log Date'})
				#continue
			elif res_id.mail_message_id.model =='purchase.order':
				type_name =''
				if res_id.mail_message_id.record_name == 'Request for Payment ':
					type_name = 'Request for Payment'
				#elif res_id.mail_message_id.record_name == 'Charity Claim ':
				#	type_name = 'Charity Claim'
				#else:
				#	type_name = 'Opex Voucher'
				#raise Warning(res_id.mail_message_id.record_name)
				obj_mail_tracking_value = self.env['mail.tracking.value'].search([('mail_message_id', '=', res_id.mail_message_id.id), ('field', '=', 'type')])
				obj_mail_tracking_value.write({'old_value_char': obj_mail_tracking_value.new_value_char, 'new_value_char': type_name})
				#obj_mail_tracking_value = self.env['mail.tracking.value'].search([('mail_message_id', '=', res_id.mail_message_id.id), ('field', '=', 'write_date')])
				#obj_mail_tracking_value.write({'field_desc': 'Log Date'})

		#raise Warning(res_id.mail_message_id.record_name)
		return res_id

