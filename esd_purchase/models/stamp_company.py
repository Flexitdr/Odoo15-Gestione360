# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class EsdStampPurchase(models.Model):
    _name = 'purchase.order.stamp'

    stamp = fields.Binary(required=True, string='stamp')
    company = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    file_name = fields.Char(string='File Name')
