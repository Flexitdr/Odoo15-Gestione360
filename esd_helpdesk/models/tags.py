# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HelpdeskTags(models.Model):
    _inherit = 'helpdesk.ticket.tag'

    department = fields.Many2one('helpdesk.ticket.team', string='Department')
