from odoo import api, fields, models

class BOMTemplate(models.Model):
    _name = 'bom.default.template'
    _description = 'BOM Default Template'

    name = fields.Char(
        string='Name',
        required=True)
    product_qty = fields.Float(
        string='Product QTY',
        required=True)
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Product UOM',
        required=True)
