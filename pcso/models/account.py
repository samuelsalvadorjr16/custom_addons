from odoo import models, fields, api

class AccountTax(models.Model):
	_inherit = 'account.tax'

	amount_type = fields.Selection(selection=[('group', 'Group of Taxes'), ('fixed', 'Fixed'), ('percent', 'Percentage of Price'), ('division', 'Percentage of Price Tax Included'), ('base_price','Percentage of Base Price - Custom')])
	is_custom_price_included = fields.Boolean(string='Custom Price Included', default=False)

	def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
		res = super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)
		if self.amount_type == 'base_price':
			if self.is_custom_price_included == True:
				base_amount = round(price_unit / 1.12,5)
				#raise Warning(round(base_amount,5) * (self.amount/100))
				return (base_amount * (self.amount/100) ) * -1
			else:
				base_amount = price_unit
				return (base_amount * (self.amount/100) )* -1
		return res