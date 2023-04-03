# -*- coding: utf-8 -*-
# Part of MERPLUS. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit ='sale.order'
    
    manual_currency_rate = fields.Float('Rate', digits=(12, 4))

    @api.onchange('manual_currency_rate','date_order','currency_id')
    def on_change_currency(self):
        company_currency = self.company_id.currency_id
        if self.currency_id.id != company_currency.id and self.currency_id.id:
            fecha_documento = self.date_order.date()
            tasa_actual = 1 / self.currency_id._get_conversion_rate(from_currency=company_currency, to_currency=self.currency_id, company=self.company_id, date=fecha_documento)
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
        else:
            self.manual_currency_rate = 0

    def _prepare_invoice(self):
        res = super(SaleOrder,self)._prepare_invoice()
        res.update({
            'manual_currency_rate':self.manual_currency_rate,
            })
        return res;

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv,self)._create_invoice(order, so_line, amount)
        if order.manual_currency_rate > 0:
            res.write({
                'manual_currency_rate':order.manual_currency_rate,
                })
        return res
