from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PaymentInvoiceLine(models.Model):
    _name = 'payment.invoice.line'

    invoice_id = fields.Many2one('account.move', 'Factura')
    line_id = fields.Many2one('account.move.line', 'Factura Lineas')
    payment_id = fields.Many2one('account.payment', 'Pago')
    partner_id = fields.Many2one(related='invoice_id.partner_id', string='Contacto')
    currency_id = fields.Many2one('res.currency', string='Moneda')
    payment_currency_id = fields.Many2one(comodel_name='res.currency', related='payment_id.currency_id', string="Moneda del pago")
    amount_total = fields.Monetary('Monto Factura', currency_field='currency_id')
    residual = fields.Monetary('Monto Pendiente', currency_field='payment_currency_id')
    amount = fields.Monetary('Monto a Pagar', currency_field='payment_currency_id', help="Entra el monto a pagar para la factura, puede ser parcial")
    invoice_date = fields.Date('Fecha Factura')
    payment_date  = fields.Date('Fecha Vencimiento')

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            if line.amount < 0:
                raise UserError(_('Monto a pagar no puede ser menor a 0! (Factura: %s)')
                                % line.invoice_id.name)

            if line.amount > line.residual:
                raise UserError(_('Monto a pagar no puede ser Mayor al monto de lo pendiente (Factura: %s)')
                                % line.invoice_id.name)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_lines = fields.One2many('payment.invoice.line', 'payment_id', 'Invoices', copy=False, help='Favor de seleccionar las facturas a pagar')
    selected_inv_total = fields.Float(compute='_compute_balance', store=True, string='Monto asignado')
    balance = fields.Float(compute='_compute_balance', string='Balance')

    @api.onchange('partner_id', 'payment_type','amount', 'currency_id','manual_currency_rate')
    def onchange_partner_id(self):
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
                                       ('account_internal_type','in', ('receivable','payable')),
                                       ('amount_residual','!=', 0)], 
                                       order="date_maturity")

            total_amount = 0
            if self.amount > 0:                
                total_amount = self.amount

            for ll in invoices:   
                invoice = ll.move_id            

                #Si es una factura de proveedor los valores vienen en negativo
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
                        'amount': min(assigned_amount, amount_residual),
                        'invoice_date': invoice.invoice_date,
                        'payment_date':ll.date_maturity
                        }

                line = PaymentLine.create(data)
                line_ids.append(line.id)
                        
            self.invoice_lines = [(6, 0, line_ids)]
        else:
            self.invoice_lines.unlink()

    @api.depends('invoice_lines', 'invoice_lines.amount', 'amount')
    def _compute_balance(self):
        for payment in self:
            total = 0.0
            for line in payment.invoice_lines:
                total += line.amount
            payment.balance = payment.amount - total
            payment.selected_inv_total = total

    @api.onchange('amount')
    def onchange_amount(self):
        ''' Function to reset/select invoices on the basis of invoice date '''
        if self.amount > 0:
            total_amount = self.amount
            for line in self.invoice_lines:
                if total_amount > 0:
                    if line.residual < total_amount:
                        line.amount = line.residual
                        total_amount -= line.residual
                    else:
                        line.amount = total_amount
                        total_amount = 0
        if (self.amount <= 0):
            for line in self.invoice_lines:
                line.amount = 0.0

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)

        self.filtered(
            lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
        )._create_paired_internal_transfer_payment()
        partials = self.conciliar()

    def conciliar (self):
        partials = 0

        #Linea del auxilar del pago
        for cuenta in self.invoice_line_ids:
            if cuenta.account_internal_type == 'receivable':
                credit_id = cuenta.id
            if cuenta.account_internal_type == 'payable':
                debit_id = cuenta.id

        #
        for partial in self.invoice_lines:
            partials_vals_list = []
            if partial.line_id.account_internal_type == 'receivable':
                debit_id = partial.line_id.id
            else:
                credit_id = partial.line_id.id

            if partial.amount > 0:
                monto_local = partial.amount
                monto_documento = partial.amount

                #Monto en moneda local, o sea de la compañia
                if self.company_currency_id.id != partial.payment_currency_id.id:
                    tasa = self.company_currency_id._get_conversion_rate(
                                            from_currency=partial.payment_currency_id, 
                                            to_currency=self.company_currency_id, 
                                            company=self.company_id, 
                                            date=self.date)
                    monto_local = monto_local * tasa

                #Monto en moneda del documento, o sea de la compañia
                if partial.currency_id.id != partial.payment_currency_id.id:
                    tasa = self.company_currency_id._get_conversion_rate(
                                            from_currency=partial.payment_currency_id, 
                                            to_currency=partial.currency_id, 
                                            company=self.company_id, 
                                            date=self.date)
                    monto_documento = monto_documento * tasa

                partials_vals_list.append({
                    'amount': monto_local,                   #Monto en moneda de la compañia
                    'debit_amount_currency': monto_documento,    #Monto en moneda del documento
                    'credit_amount_currency': monto_documento,   #Monto en moneda del documento
                    'debit_move_id': debit_id,
                    'credit_move_id': credit_id,
                })
                partials = self.env['account.partial.reconcile'].create(partials_vals_list)
            else:
                partial.unlink()
        return partials

    @api.constrains('amount', 'invoice_lines')
    def _check_invoice_amount(self):
        ''' Function to validate if user has selected more amount invoices than payment '''
        for payment in self:
            total = 0.0
            if payment.invoice_lines:
                for line in payment.invoice_lines:
                    total += line.amount
                if total > payment.amount:
                    raise UserError(_('No puedes asignar mas valor en factura que el monto a pagar'))
