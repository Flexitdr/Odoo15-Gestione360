# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class CommissionLine(models.Model):
    _name = 'commission.line'
    _description = 'Commission Line'
    _order = 'id desc'

    date = fields.Date(string='Date', required=False, default=datetime.today())
    profile_id = fields.Many2one(comodel_name='profile.commission', string='Profile', required=False)
    user_id = fields.Many2one(comodel_name='res.users', string='User', required=False)
    manager_id = fields.Many2one(comodel_name='res.users', string='Manager', required=False)
    invoice_id = fields.Many2one(comodel_name='account.move', string='Invoice', required=False)
    payment_id = fields.Many2one(comodel_name='account.payment', string='Payment', required=False)
    payment = fields.Char(string='Payment', required=False)
    payment_int_id = fields.Integer(string='Payment ID', required=False)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', required=False)
    net_amount = fields.Float(string='Net Amount', required=False)
    payment_amount = fields.Float(string='Payment Amount', required=False)
    percentage = fields.Float(string='Percentage %', required=False)
    commission_amount = fields.Float(string='Commission Amount', required=False)
    day_count = fields.Integer(string='Day Count',required=False)
    date_payment = fields.Date(string='Date Payment',required=False)
    date_invoice = fields.Date(string='Date Invoice',required=False)
    state = fields.Selection(string='State',selection=[('generated', 'Generated'),
                                                       ('validated', 'Validated'),
                                                       ('cancel', 'Cancelled'),
                                                       ('partial', 'Partial'),
                                                       ('paid', 'Paid'), ], required=False, deafult='generated')
    is_reverse = fields.Boolean(string='Is Reverse', required=False)
    external_provider = fields.Boolean(string='External Provider')
    from_reverse = fields.Boolean(string='From Reverse', required=False)
    commission_pay_form_id = fields.Many2one(comodel_name='commission.pay.form', string='Commission Pay Form', required=False)
    commission_line_to_revert_id = fields.Many2one(comodel_name='commission.line', string='Commission Line To Revert', required=False)
    company_id = fields.Many2one(comodel_name='res.company', string='Company_id', required=False, default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', required=False, default=lambda self: self.env.user.company_id.currency_id.id)
    is_financing = fields.Boolean(string='Is Financing', required=False)
    fee_qty = fields.Integer(string='Fee Quantity', required=False)