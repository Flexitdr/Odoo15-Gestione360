from odoo import _, api, models, fields, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta


class SubscriptionPayment(models.Model):
    _name = 'subscription.payment.line'

    name = fields.Char(string='Name', required=False)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', required=False)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=False)
    reference_code = fields.Char(string='Reference')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=False, default=lambda self: self.env.user.company_id)
    recurring_price = fields.Float(string="Recurring Price")
    plan_id = fields.Many2one('subscription.package.plan', string='Plan')
    plan_duration = fields.Date(string='Duration')
    equipment = fields.Char(string='Equipment')
    payment_format = fields.Char(string='Payment Format')
    state = fields.Selection(string='State', selection=[('generated', 'Generated'),
                                                        ('created', 'Created'),
                                                        ('paid', 'Paid')], required=False, default='created')
    qty_fee = fields.Char(string='Quantity')
    invoice_code = fields.Char(string='Invoice Code', required=False)
    product_qty = fields.Char(string='Invoice Quantity', required=False)

    def _generated_invoices(self):
        for record in self:
            record.state = 'generated'
