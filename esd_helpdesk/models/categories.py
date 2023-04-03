# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HelpdeskCategories(models.Model):
    _inherit = 'helpdesk.ticket.category'

    department = fields.Many2one('helpdesk.ticket.team', string='Department')
