# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    commission_pay = fields.Boolean(string='Commission')


