# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Production(models.Model):
    _inherit = 'mrp.production'

    employee_responsable_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Employee Responsable')