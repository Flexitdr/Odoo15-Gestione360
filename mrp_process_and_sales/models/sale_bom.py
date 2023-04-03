from odoo import api, fields, models, _


class SaleOrderMRPBom(models.Model):
    _name = 'sale.order.mrp.bom'
    _description = 'Sale Order MRP'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Component',
        required=False)
    name = fields.Char(
        string='Name',
        required=False)
    product_qty = fields.Float(
        string='Product QTY',
        required=True)
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Product UOM',
        required=True)
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Line',
        required=False, domain="[('has_bom', '=', True)]")
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale',
        required=False)
    wizard_id = fields.Many2one(
        comodel_name='create.bom.sale',
        string='Wizard',
        required=False)

    @api.onchange('name')
    def _onchange_name(self):
        self.product_id.name = self.name + " " + self.sale_line_id.name_brand

    def unlink(self):

        for rec in self:
            rec.product_id.product_tmpl_id.unlink()

        return super(SaleOrderMRPBom, self).unlink()

class CreateBOMSale(models.Model):
    _name = 'create.bom.sale'
    _description = 'Create BOM From Sale Wizard'

    name = fields.Char(
        string='Name of Brand',
        required=False)
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Line',
        required=False)
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale',
        required=False)
    brand_id = fields.Many2one(
        comodel_name='sale.product.brand',
        string='Brand',
        required=False)
    line_ids = fields.One2many(
        comodel_name='sale.order.mrp.bom',
        inverse_name='wizard_id',
        string='Line',
        required=False)
    state = fields.Selection(
        related='order_id.state', string='Order Status', copy=False, store=True)

    @api.model
    def create(self, values):
        # Add code here
        ID = super(CreateBOMSale, self).create(values)

        ID.sale_line_id.bom_to_create_id = ID

        return ID
