# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError
import json
import logging
from datetime import timedelta
from collections import defaultdict
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    subs_field = fields.Char(string='Subscription Line')