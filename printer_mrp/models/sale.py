from odoo import api, fields, models, _ 

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_operations(self, line, bom):

        for operation in line.workcenter_id.operation_ids:
            bom.operation_ids.create({
                'bom_id': bom.id,
                'name': operation.name,
                'workcenter_id': line.workcenter_id.id,
                'time_mode': 'auto'
            })
    def create_production_order(self):
        for line in self.order_line.filtered(lambda r: r.has_bom):

            bom_sale = self.env['create.bom.sale'].search([('sale_line_id', '=', line.id)], limit=1)

            product_template = self.env['product.template'].create({'name': line.product_id.name + ": " + line.name_brand,
                                                                    'uom_id': line.product_uom.id,
                                                                    'uom_po_id': line.product_uom.id,
                                                                    'detailed_type': 'product'})
            line.product_brand_id = product_template

            bom = self.env['mrp.bom'].create({
                'product_tmpl_id': product_template.id,
            })

            operations = self.create_operations(line, bom)

            for line_bom in bom_sale.line_ids:
                bom.bom_line_ids.create({
                    'product_id': line_bom.product_id.id,
                    'product_qty': line_bom.product_qty,
                    'product_uom_id': line_bom.product_uom_id.id,
                    'bom_id': bom.id
                })

            bom.bom_line_ids.create({
                'product_id': line.product_id.id,
                'product_qty': 1,
                'product_uom_id': line.product_id.uom_id.id,
                'bom_id': bom.id
            })

            self.env['mrp.production'].create_mrp_from_pos([product_template.product_variant_id], line)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    address_id = fields.Many2one(
        comodel_name='res.partner',
        string='Address',
        required=False, domain="[('parent_id', '=', order_partner_id)]")
    committed_date = fields.Datetime(
        string='Committed Date', 
        required=True)
    includes_sample = fields.Selection(
        string='Includes Sample',
        selection=[('yes', 'Yes'),
                   ('not', 'Not'), ],
        required=False, )
    workcenter_id = fields.Many2one(
        comodel_name='mrp.workcenter',
        string='Department',
        required=False)
    send_art = fields.Selection(
        string='Send Art',
        selection=[('email', 'Email'),
                   ('customer', 'Customer Address'),
                   ],
        required=False, )
    logo = fields.Selection(
        string='Logo',
        selection=[('many', 'Many'),
                   ('one', 'One'),
                   ],
        required=False, )
