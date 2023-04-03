from odoo import api, fields, models 
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class FeePlan(models.Model):
    _name = 'esd.payment.plan.fee'
    _description = 'Fee'

    name = fields.Char(
        string='Name',
        required=False, compute='_compute_name')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=False)
    payment_plan_id = fields.Many2one(
        comodel_name='esd.payment.plan',
        string='Payment Plan',
        required=False)
    date = fields.Date(
        string='Date', 
        required=False)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=False)
    amount_financed = fields.Float(
        string='Amount Financed',
        required=False)
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale',
        required=False)
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Line',
        required=False)
    product_id = fields.Many2one(
        'product.product', string='Product',)
    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice',
        required=False)
    fee_ids = fields.One2many(
        comodel_name='esd.fee',
        inverse_name='fee_plan_id',
        string='Fee',
        required=False)
    state = fields.Selection(
        string='State',
        selection=[('created', 'Created'),
                   ('running', 'Running'),
                   ('closed', 'Close'),
                   ],
        required=False, default='running')


    @api.depends('sale_id', 'partner_id', 'product_id')
    def _compute_name(self):

        for rec in self:

            name = 'Error: Sale Name'

            try:
                name = rec.sale_id.name + ": (" + rec.partner_id.name + ": " + rec.product_id.name + ")"
            except TypeError:
                pass


            rec.name = name

    def create_plan_fee(self):

        count = 0

        fee_line = []
        if self.sale_line_id.installation_required:
            amount_fee = self.amount_financed / self.payment_plan_id.qty_payment

            while count < self.payment_plan_id.qty_payment:
                date_payment = self.date + relativedelta(months=count)

                qty_fee_calculation = "{}/{}".format(count+1, self.payment_plan_id.qty_payment)

                self.fee_ids.create({
                    'fee_plan_id': self.id,
                    'partner_id': self.partner_id.id,
                    'payment_date': date_payment,
                    'currency_id': self.currency_id.id,
                    'amount_to_pay': amount_fee,
                    'sale_id': self.sale_id.id,
                    'sale_line_id': self.sale_line_id.id,
                    'qty_fee': qty_fee_calculation
                })

                count += 1


class Fee(models.Model):
    _name = 'esd.fee'
    _description = 'Fee'

    fee_plan_id = fields.Many2one(
        comodel_name='esd.payment.plan.fee',
        string='Fee Plan',
        required=False)
    name = fields.Char(string='Name', related='fee_plan_id.name')

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=False)
    payment_date = fields.Date(
        string='Payment Date',
        required=False)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=False)
    amount_to_pay = fields.Float(
        string='Amount Financed',
        required=False)
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale',
        required=False)
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Line',
        required=False)
    qty_fee = fields.Char(string="Qyt Fee")
    state = fields.Selection(
        string='State',
        selection=[('created', 'Created'),
                   ('generated', 'Generated'),
                   ('paid', 'Paid'),
                   ],
        required=False, default='created')
