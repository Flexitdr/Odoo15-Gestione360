# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class ProfileCommission(models.Model):
    _name = 'profile.commission'
    _description = 'Profile Commission'

    name = fields.Char(string='Name', required=True)
    type_profile = fields.Selection(string='Type Profile', selection=[('own_payments', 'Own Payment'),
                                                                      ('own_sales_payments', 'Own Sales Payments'),
                                                                      ('other_payments', 'Payments of Other'),
                                                                      ('products', 'Products'),
                                                                      ('product_category', 'Product Category')], required=True,)

    for_own_sales = fields.Boolean(string='For Own Sales', required=False)
    user_ids = fields.Many2many(comodel_name='res.users', relation='profile_commission_users_rel',
                                column1='profile_id', column2='user_id', string='Users')
    partners_ids = fields.Many2many(comodel_name='res.partner', relation='profile_commission_partner_rel',
                                column1='profile_partner_id', column2='partner_id', string='Partners')
    external_provider = fields.Boolean(string='External Provider')
    salesperson_ids = fields.Many2many(comodel_name='res.users', relation='profile_commission_salespersons_rel',
                                       column1='profile_id', column2='salesperson_id', string='Salesperson')
    commission_period_line_ids = fields.One2many(comodel_name='commission.period.line', inverse_name='profile_id',
                                                 string='Commission Period Line', required=False)
    product_category_ids = fields.Many2many(comodel_name='product.category', string='Product Category')
    company_id = fields.Many2one(comodel_name='res.company', string='Company_id',
                                 required=False, default=lambda self: self.env.user.company_id.id)
    commission_fee_ids = fields.One2many(comodel_name='commission.period.line', inverse_name='profile_id',
                                                 string='Commissions Fee', required=False)

    def calculate_commission(self, payment_date, invoice_date):

        difference = payment_date - invoice_date

        days = difference.days

        if days < 0:
            days = 0

        period = self.commission_period_line_ids.filtered(lambda r: r.from_days <= days <= r.to_days)

        return {'days_count': days, 'percentage': period.percentage}

