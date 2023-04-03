from odoo import api, fields, models, _
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.exceptions import ValidationError, UserError
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create_mrp_from_pos(self, products, sale_line):
        product_ids = []
        if products:
            for product in products:
                flag = 1
                if product_ids:
                    for product_id in product_ids:
                        if product_id['id'] == product['id']:
                            product_id['qty'] += product['qty']
                            flag = 0
                if flag:
                    product_ids.append(product)
            for prod in product_ids:
                # if prod['qty'] > 0:
                product = self.env['product.product'].search([('id', '=', prod['id'])])
                bom_count = self.env['mrp.bom'].search([('product_tmpl_id', '=', prod['product_tmpl_id'].id)])
                if bom_count:
                    bom_temp = self.env['mrp.bom'].search([('product_tmpl_id', '=', prod['product_tmpl_id'].id),
                                                           ('product_id', '=', False)])
                    bom_prod = self.env['mrp.bom'].search([('product_id', '=', prod['id'])])
                    if bom_prod:
                        bom = bom_prod[0]
                    elif bom_temp:
                        bom = bom_temp[0]
                    else:
                        bom = []
                    if bom:
                        vals = {
                            'origin': sale_line.order_id.name,
                            'state': 'confirmed',
                            'product_id': prod['id'],
                            'product_tmpl_id': prod['product_tmpl_id'].id,
                            'product_uom_id': prod['uom_id'].id,
                            'product_qty': sale_line.product_uom_qty,
                            'bom_id': bom.id,
                            'qty_producing': sale_line.product_uom_qty,
                            # 'move_finished_ids': [0, 0,{
                            #     'product_id': product.id,
                            #     'product_uom': product.uom_id.id,
                            #     'product_uom_qty': sale_line.product_uom_qty,
                            #     'location_id': product.with_company(self.company_id.id).property_stock_production.id,
                            #     'location_dest_id': 8,
                            #     'name': product.name,
                            #     # 'byproduct_id': False,
                            # }]
                        }
                        mrp_order = self.sudo().create(vals)
                        list_value = []
                        for bom_line in mrp_order.bom_id.bom_line_ids:
                            list_value.append((0, 0, {
                                'raw_material_production_id': mrp_order.id,
                                'name': mrp_order.name,
                                'product_id': bom_line.product_id.id,
                                'product_uom': bom_line.product_uom_id.id,
                                'product_uom_qty': bom_line.product_qty * mrp_order.product_qty,
                                'picking_type_id': mrp_order.picking_type_id.id,
                                'location_id': mrp_order.location_src_id.id,
                                'location_dest_id': bom_line.product_id.with_company(self.company_id.id).property_stock_production.id,
                                'company_id': mrp_order.company_id.id,
                            }))

                        mrp_order.update({'move_raw_ids':list_value})
                        mrp_order._create_update_move_finished()
                        # mrp_order.onchange(vals, '')
        return mrp_order