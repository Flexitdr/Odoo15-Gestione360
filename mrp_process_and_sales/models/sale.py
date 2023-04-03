from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError
import json
import logging
from datetime import timedelta
from collections import defaultdict
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_bom_branding = fields.Boolean(
        string='Has branding',
        required=False)
    mrp_bom_ids = fields.One2many(
        comodel_name='sale.order.mrp.bom',
        inverse_name='order_id',
        string='MRP BOM',
        required=False)

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

    def create_in_picking(self):

        transfer = self.env['stock.picking'].create({
            'picking_type_id': self.warehouse_id.in_type_id.id,
            'location_id': self.warehouse_id.in_type_id.default_location_src_id.id,
            'location_dest_id': self.warehouse_id.in_type_id.default_location_dest_id.id,
            'partner_id': self.partner_id.id,
            'sale_id': self.id
        })

        for line in self.order_line.filtered(lambda r: r.has_bom):
            for product in line.bom_to_create_id.line_ids:
                transfer['move_lines'] = [(0, 0, {
                    'product_uom_qty': line.product_uom_qty * product.product_qty,
                    'product_id': product.product_id.id,
                    "product_uom": product.product_id.uom_id.id,
                    'location_id': self.warehouse_id.in_type_id.default_location_src_id.id,
                    'location_dest_id': self.warehouse_id.in_type_id.default_location_dest_id.id,
                    'name': product.name
                })]

        transfer.action_confirm()

    def action_confirm(self):
        if self.has_bom_branding:
            self.create_production_order()
            self.create_in_picking()

        super().action_confirm()

        picking_out = self.picking_ids.filtered(lambda r: r.picking_type_id.code == 'outgoing')

        for picking in picking_out:
            picking.state = 'draft'
            moves = picking.move_lines.filtered(lambda r: r.product_id == r.sale_line_id.product_id \
                                                          and r.sale_line_id.has_bom)

            for move in moves:
                move.state = 'draft'

            moves.unlink()
    def _action_confirm(self):
        # self.order_line._action_launch_stock_rule()
        self.order_line._action_launch_stock_rule_with_brand()
        return super(SaleOrder, self)._action_confirm()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    has_bom = fields.Boolean(
        string='Has BOM',
        required=False)
    name_brand = fields.Char(
        string='Name of Brand',
        required=False)
    sale_brand_id = fields.Many2one(
        comodel_name='sale.product.brand',
        string='Sale Brand',
        required=False, domain="[('partner_id', '=', order_partner_id)]")
    bom_to_create_id = fields.Many2one(
        comodel_name='create.bom.sale',
        string='BOM to Create',
        required=False)
    product_brand_id = fields.Many2one(
        comodel_name='product.template',
        string='Product brand',
        required=False)

    def create_bom(self):

        if not self.bom_to_create_id:

            default_bom = self.env['bom.default.template'].search([])

            lines_bom = []

            for line in default_bom:
                product_name = line.name + " " + self.name_brand
                product_template = self.env['product.template'].create({'name': product_name,
                                                                        'uom_id': line.product_uom_id.id,
                                                                        'uom_po_id': line.product_uom_id.id,
                                                                        'detailed_type': 'product'})
                # raise ValidationError(_(product_template.product_variant_id))

                lines_bom.append([0, 0, {
                    'name': line.name,
                    'product_id': product_template.product_variant_id.id,
                    'product_qty': line.product_qty,
                    'product_uom_id': line.product_uom_id.id
                }])

            bom = self.env['create.bom.sale'].create({

                'sale_line_id': self.id,
                'order_id': self.order_id.id,
                'line_ids': lines_bom
            })
        else:
            bom = self.bom_to_create_id

        return {
            'name': _('Create BOM'),
            'type': 'ir.actions.act_window',
            'res_model': 'create.bom.sale',
            'view_mode': 'form',
            'res_id': bom.id,
            'target': 'new'
        }


    def _action_launch_stock_rule_with_brand(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        if self._context.get("skip_procurement"):
            return True
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.state != 'sale' or not line.product_brand_id.product_variant_id.type in ('consu', 'product'):
                continue
            # qty = line._get_qty_procurement(previous_product_uom_qty)
            qty = line.product_uom_qty
            # if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
            #     continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            line_uom = line.product_uom
            quant_uom = line.product_brand_id.product_variant_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(line.product_uom_qty, quant_uom)
            procurements.append(self.env['procurement.group'].Procurement(
                line.product_brand_id.product_variant_id, line.product_uom_qty, procurement_uom,
                line.order_id.partner_shipping_id.property_stock_customer,
                line.product_brand_id.product_variant_id.display_name, line.order_id.name, line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)

        # This next block is currently needed only because the scheduler trigger is done by picking confirmation rather than stock.move confirmation
        # orders = self.mapped('order_id')
        # for order in orders:
        #     pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
        #     if pickings_to_confirm:
        #         # Trigger the Scheduler for Pickings
        #         pickings_to_confirm.action_confirm()
        return True

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
            if line.qty_delivered_method == 'stock_move' and line.has_bom:
                qty = 0.0
                outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
                for move in outgoing_moves:
                    if move.state != 'done':
                        continue
                    qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom,
                                                              rounding_method='HALF-UP')
                for move in incoming_moves:
                    if move.state != 'done':
                        continue
                    qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom,
                                                              rounding_method='HALF-UP')
                line.qty_delivered = qty

    def _get_outgoing_incoming_moves(self):
        outgoing_moves = self.env['stock.move']
        incoming_moves = self.env['stock.move']

        moves = self.move_ids.filtered(
            lambda r: r.state != 'cancel' and not r.scrapped and self.product_brand_id.product_variant_id == r.product_id)
        if self._context.get('accrual_entry_date'):
            moves = moves.filtered(
                lambda r: fields.Date.context_today(r, r.date) <= self._context['accrual_entry_date'])

        for move in moves:
            if move.location_dest_id.usage == "customer":
                if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                    outgoing_moves |= move
            elif move.location_dest_id.usage != "customer" and move.to_refund:
                incoming_moves |= move

        return outgoing_moves, incoming_moves

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'untaxed_amount_to_invoice')
    def _compute_qty_invoiced(self):
        """
        Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
        that this is the case only if the refund is generated from the SO and that is intentional: if
        a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
        it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
        """
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state != 'cancel' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    if invoice_line.move_id.move_type == 'out_invoice':
                        qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                      line.product_uom)
                    elif invoice_line.move_id.move_type == 'out_refund':
                        qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                      line.product_uom)
            line.qty_invoiced = qty_invoiced