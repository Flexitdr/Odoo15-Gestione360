# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    is_commission = fields.Boolean(string='Is Commission')
