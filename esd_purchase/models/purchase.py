# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class EsdPurchase(models.Model):
    _inherit = 'purchase.order'

    def set_notes_field(self):
        company_comment = self.env['purchase.order.comments'].search([('company', '=', self.env.company.id)])
        return company_comment.comments

    def set_stamp_field(self):
        company_stamp = self.env['purchase.order.stamp'].search([('company', '=', self.env.company.id)])
        return company_stamp.stamp

    subject = fields.Char(required=True, string='Subject')
    notes = fields.Html('Terms and Conditions', default=set_notes_field, readonly=True)
    stamp = fields.Binary(required=True, string='stamp', default=set_stamp_field)


class EsdPurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float(string='Discount')

    @api.onchange('discount')
    def calculate_discount(self):
        discount_mount = self.discount / 100
        discount = self.price_unit - (self.price_unit * discount_mount)
        self.price_unit = discount
