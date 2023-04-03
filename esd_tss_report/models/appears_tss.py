from odoo import models, fields, api


class InheritAppearsTss(models.Model):
    _inherit = 'hr.salary.rule'

    appears_on_tss = fields.Boolean('Appears_on_tss')
    show_in_header = fields.Boolean('Show in Header')
    where_sum_id = fields.Many2one('hr.salary.rule', string='Where sum salary rule', index=True)


# class WhereSum(models.Model):
#     _name = 'where.sum'
#
#     where_sum = fields.Many2one('hr.salary.rule', string="Salary rules")
