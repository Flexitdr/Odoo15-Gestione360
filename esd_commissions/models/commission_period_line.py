# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class CommissionPeriodLine(models.Model):
    _name = 'commission.period.line'
    _description = 'Commission Period Line'

    name = fields.Char(string='Name', required=False)
    from_days = fields.Integer(string='From Days', required=False)
    to_days = fields.Integer(string='To Days', required=False)
    percentage = fields.Float(string='Percentage %', required=False)
    profile_id = fields.Many2one(comodel_name='profile.commission', string='Profile', required=False)
    fee_qty = fields.Integer(string='Fee Quantity',required=False)

    @api.depends('from_days', 'to_days')
    def _compute_name(self):

        for rec in self:
            rec.name = "%s - %s" % (rec.from_days, rec.to_days)
