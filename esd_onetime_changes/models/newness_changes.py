from odoo import models, fields, api


class NewnessChanges(models.Model):
    _name = 'newness.changes'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Code', required=True)
    category = fields.Selection(selection=[('contribution', 'Contribution'), ('incomes', 'Incomes'),
                                           ('deduction', 'Deduction')], required=True)
