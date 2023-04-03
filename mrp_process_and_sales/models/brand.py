from odoo import api, fields, models, _

class Brand(models.Model):
    _name = 'sale.product.brand'
    _description = 'Brand'

    name = fields.Char(
        string='Name',
        required=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=False, default=lambda self: self.env.company)
    code = fields.Char(
        string='Code',
        required=True)
