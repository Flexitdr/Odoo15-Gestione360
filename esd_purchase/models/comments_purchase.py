# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class EsdCommentPurchase(models.Model):
    _name = 'purchase.order.comments'

    comments = fields.Text(required=True, string='Comments')
    company = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
