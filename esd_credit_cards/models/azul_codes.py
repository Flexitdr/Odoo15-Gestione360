# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AzulCodes(models.Model):
    _name = 'azul.codes'
    _order = 'id desc'

    def _default_partner(self):
        partner_id = self.env.context.get('partner_id')
        return self.env['res.partner'].search([('id', '=', partner_id)]).id

    name = fields.Char(string='Code', required=True)
    partner = fields.Many2one('res.partner', required=True, default=_default_partner)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Azul Code already exists!"),
    ]
