from odoo import api, fields, models

class OperationWorkcenter(models.Model):
    _name = 'operation.workcenter'
    _description = 'Operation Workcenter'

    name = fields.Char(
        string='Name',
        required=True)
    workcenter_id = fields.Many2one(
        comodel_name='mrp.workcenter',
        string='Workcenter',
        required=False)

class Workcenter(models.Model):
    _inherit = 'mrp.workcenter'

    operation_ids = fields.One2many(
        comodel_name='operation.workcenter',
        inverse_name='workcenter_id',
        string='Operations',
        required=False)


