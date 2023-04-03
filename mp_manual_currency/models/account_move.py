# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_move(models.Model):
	_inherit ='account.move'

	manual_currency_rate = fields.Float('Rate', digits=(12, 4))

	@api.onchange('manual_currency_rate','invoice_date','currency_id')
	def on_change_currency(self):
		if self.currency_id.id != self.company_currency_id.id and self.currency_id.id:
			if self.invoice_date:
				fecha_documento = self.invoice_date
			else:
				fecha_documento = self.write_date.date()
			tasa_actual = 1 / self.currency_id._get_conversion_rate(from_currency=self.company_currency_id, to_currency=self.currency_id, company=self.company_id, date=fecha_documento)
			if self.manual_currency_rate <= 0:
				self.manual_currency_rate = tasa_actual
			elif self.manual_currency_rate != tasa_actual:
				tasa_nueva = {
					'name': fecha_documento,
					'company_id': self.company_id.id,
					'company_rate': 1 / self.manual_currency_rate,
					'inverse_company_rate': self.manual_currency_rate
				}
				rate_val =[(0, 0, tasa_nueva)]
				for lin in self.currency_id.rate_ids:
					if lin.name == fecha_documento:
						rate_val =[(1, lin.id, tasa_nueva)]
						break
				self.currency_id.write({
					'rate_ids': rate_val
				})
				self._onchange_currency() 
		else:
			self.manual_currency_rate = 0
