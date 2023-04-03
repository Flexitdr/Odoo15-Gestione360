# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api, _


class ResPartnerCode(models.Model):
    _inherit = 'res.partner'

    azul_code = fields.Many2many('azul.codes', string="Azul Code", domain="[('partner.id', '=', id)]")
