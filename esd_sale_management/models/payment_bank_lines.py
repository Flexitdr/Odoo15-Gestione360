from odoo import api, fields, models

class PaymentBankLine(models.Model):
    _name = 'payment.bank.line'
    _description = 'Payment Bank Line'

    name = fields.Char(
        string='Name',
        required=False, related='product_id.name')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=False)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=False)
    bank_id = fields.Many2one(
        comodel_name='res.partner',
        string='Bank',
        required=False)
    bank_amount = fields.Float(
        string='Bank Amount',
        required=False)
    customer_amount = fields.Float(
        string='Customer Amount',
        required=False)
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale',
        required=False)
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Line',
        required=False)
    state = fields.Selection(
        string='State',
        selection=[('not-invoiced', 'Not Invoiced'),
                   ('invoiced', 'Invoiced'),
                   ],
        required=False, )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=False, default=lambda self: self.env.user.company_id)
    approbation_code = fields.Char(
        string='Approbation Code',
        required=False)

    @api.model
    def create_invoice(self, records):

        bank_ids = self.env['res.partner'].search([('is_bank', '=', True)])

        for bank in bank_ids:
            lines = records.filtered(lambda r: r.bank_id.id == bank.id)

            invoice_lines = []

            for line in lines:
                line.state = 'invoiced'

                invoice_lines.append((0, 0, {
                    'product_id': line.sale_line_id.product_id.id,
                    'name': line.sale_line_id.name,
                    'price_unit': line.bank_amount,
                    'tax_ids': []
                }))

            self.env['account.move'].create(
                {
                    'move_type': 'out_invoice',
                    'date': fields.Date.today(),
                    'invoice_date': fields.Date.today(),
                    'partner_id': bank.id,
                    'currency_id': bank.currency_id.id,
                    'invoice_line_ids': invoice_lines,
                    'journal_id': 1,
                })