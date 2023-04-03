from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_brand_id = fields.Many2one(
        comodel_name='sale.product.brand',
        string='Sale brand',
        required=False)
