# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
