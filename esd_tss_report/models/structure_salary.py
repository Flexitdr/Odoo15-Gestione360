# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api, _


class StructureSalary(models.Model):
    _inherit = 'hr.payslip.run'

    structure_salary = fields.Many2one('hr.payroll.structure', string="Structure Salary", required=True)
