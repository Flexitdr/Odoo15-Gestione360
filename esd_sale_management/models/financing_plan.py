from odoo import api, fields, models

class FinancingTime(models.Model):
    _name = 'esd.financing.plan'
    _description = 'Finance Time'

    name = fields.Char(
        string='Name',
        required=True)
    qty_month = fields.Integer(
        string='Qty Month',
        required=True)
    payment_plan_ids = fields.One2many(
        comodel_name='esd.payment.plan',
        inverse_name='financing_time_id',
        string='Payment Plan',
        required=False)

class PaymentPlan(models.Model):
    _name = 'esd.payment.plan'
    _description = 'Payment Plan'

    name = fields.Char(
        string='Name',
        required=True)
    code = fields.Char(
        string='Code',
        required=True, max=5)
    qty_payment = fields.Integer(
        string='Qty Payments',
        required=True)
    financing_time_id = fields.Many2one(
        comodel_name='esd.financing.plan',
        string='Financing Time',
        required=False)