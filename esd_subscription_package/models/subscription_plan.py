# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class SubscriptionPlan(models.Model):

    _inherit = 'subscription.package.plan'

    product_line = fields.Many2many(comodel_name='product.product', string='Subscription Product')