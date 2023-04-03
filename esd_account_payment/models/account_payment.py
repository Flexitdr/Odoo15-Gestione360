from odoo import _, api, Command, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    not_distribute = fields.Boolean(string='Not Distribute', default=False)

    @api.depends('invoice_lines', 'invoice_lines.amount', 'amount')
    def _compute_balance(self):

        payment = super()._compute_balance()

        for pay in self:

            if pay.not_distribute:

                pay.balance = pay.amount
                pay.selected_inv_total = 0
            else:
                return payment

    @api.onchange('partner_id', 'payment_type', 'amount', 'currency_id', 'manual_currency_rate')
    def onchange_partner_id(self):

        invoices_to_pay = super().onchange_partner_id()

        if self.not_distribute:

            Invoice = self.env['account.move.line']
            PaymentLine = self.env['payment.invoice.line']

            type = ''
            if self.payment_type == 'outbound' and self.partner_type == 'supplier':
                type = 'in_invoice'
            elif self.payment_type == 'inbound' and self.partner_type == 'customer':
                type = 'out_invoice'
            if self.partner_id and type:
                line_ids = []
                invoices = Invoice.search([('partner_id.id', '=', self.partner_id.id),
                                           ('move_id.state', 'in', ('posted',)),
                                           ('move_id.move_type', '=', type),
                                           ('account_internal_type', 'in', ('receivable', 'payable')),
                                           ('amount_residual', '!=', 0)],
                                          order="date_maturity")

                total_amount = 0
                if self.amount > 0:
                    total_amount = self.amount

                for ll in invoices:
                    invoice = ll.move_id

                    # Si es una factura de proveedor los valores vienen en negativo
                    signo = -1 if ll.account_internal_type == 'payable' else 1
                    amount_total = ll.amount_currency * signo
                    amount_residual = ll.amount_residual_currency * signo

                    ''' moneda documento -> moneda de pago'''
                    if ll.currency_id.id != self.currency_id.id:
                        tasa = self.company_currency_id._get_conversion_rate(
                            from_currency=ll.currency_id,
                            to_currency=self.currency_id,
                            company=self.company_id,
                            date=self.date)
                        amount_residual = amount_residual * tasa

                    if amount_residual < total_amount:
                        assigned_amount = amount_total
                        total_amount -= min(amount_total, amount_residual)
                    else:
                        assigned_amount = total_amount
                        total_amount = 0

                    data = {'invoice_id': invoice.id,
                            'line_id': ll.id,
                            'currency_id': ll.currency_id.id,
                            'payment_currency_id': self.currency_id,
                            'amount_total': amount_total,
                            'residual': amount_residual,
                            'amount': 0,
                            'invoice_date': invoice.invoice_date,
                            'payment_date': ll.date_maturity
                            }

                    line = PaymentLine.create(data)
                    line_ids.append(line.id)

                self.invoice_lines = [(6, 0, line_ids)]

        else:
            return invoices_to_pay
