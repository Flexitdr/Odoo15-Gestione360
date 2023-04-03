# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

from odoo.addons.payment import utils as payment_utils

class SaleLine(models.Model):
    _inherit = 'sale.order.line'

    financing_id = fields.Many2one(
        comodel_name='esd.financing.plan',
        string='Financing',
        required=False)
    payment_plan_id = fields.Many2one(
        comodel_name='esd.payment.plan',
        string='Payment Plan',
        required=False, domain="[('financing_time_id', '=', financing_id)]")
    bank_amount = fields.Float(
        string='Bank Amount',
        required=False)
    customer_amount = fields.Float(
        string='Customer Amount',
        required=False, compute='_compute_customer_amount')
    group_id = fields.Integer(
        string='Group',
        required=True)
    is_financing_sale = fields.Boolean(
        string='Is Financing',
        required=False, related='order_id.is_financing_sale')
    is_pay_by_bank = fields.Boolean(
        string='Is Pay By Bank',
        required=False, related='order_id.is_pay_by_bank')
    fee_plan_id = fields.Many2one(
        comodel_name='esd.payment.plan.fee',
        string='Fee Plan',
        required=False)
    product_type_related = fields.Char()

    @api.onchange('product_id')
    def change_product_service_type(self):

        for rec in self:
            product = self.env['product.product'].search([('id', '=', rec.product_id.id)])

            rec.product_type_related = product.detailed_type

    @api.onchange('product_id')
    def change_group_id(self):
        count = 0
        list_group_id = []
        for rec in self:

            if count == 0 and len(self.order_id.order_line) > 1:

                for res in self.order_id.order_line:

                    list_group_id.append(res.group_id)

                    list_group_id.sort()

                    count = list_group_id[-1]

                if rec.installation_required:
                    count += 1
                    rec.group_id = count

                else:
                    for res in self.order_id.order_line:
                        list_group_id.append(res.group_id)

                        list_group_id.sort()

                        count = list_group_id[-1]
                        rec.group_id = count

                        count += 1

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'payment_plan_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if not line.payment_plan_id:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
                if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                        'account.group_account_manager'):
                    line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
            else:
                price = (line.price_unit / line.payment_plan_id.qty_payment) * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
                if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                        'account.group_account_manager'):
                    line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.onchange('product_id')
    def _onchange_esd_product_id_2(self):
        if self.order_id.offer_id:
            if self.order_id.offer_id.line_ids:
                line = self.order_id.offer_id.line_ids.filtered(lambda r: r.product_id.id == self.product_id.id)
                if line:
                    self.discount = line[0].discount

    @api.depends('price_subtotal', 'bank_amount')
    def _compute_customer_amount(self):

        for rec in self:
            rec.customer_amount = rec.price_subtotal - rec.bank_amount

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.
        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        if self.payment_plan_id:
            res = {
                'display_type': self.display_type,
                'sequence': self.sequence,
                'name': self.name,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'quantity': self.qty_to_invoice,
                'discount': self.discount,
                'price_unit': self.price_subtotal,
                'tax_ids': [(6, 0, self.tax_id.ids)],
                'sale_line_ids': [(4, self.id)],
            }
        else:
            res = {
                'display_type': self.display_type,
                'sequence': self.sequence,
                'name': self.name,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom.id,
                'quantity': self.qty_to_invoice,
                'discount': self.discount,
                'price_unit': self.price_unit,
                'tax_ids': [(6, 0, self.tax_id.ids)],
                'sale_line_ids': [(4, self.id)],
            }
        if not self.analytic_tag_ids and not self.display_type:
            res['analytic_tag_ids'] = []
        if self.order_id.analytic_account_id and not self.display_type:
            res['analytic_account_id'] = self.order_id.analytic_account_id.id
        if self.analytic_tag_ids and not self.display_type:
            res['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_financing_sale = fields.Boolean(
        string='Is Financing',
        required=False)
    is_pay_by_bank = fields.Boolean(
        string='Is Pay By Bank',
        required=False, related='offer_id.payment_by_bank')
    bank_id = fields.Many2one(
        comodel_name='res.partner',
        string='Bank',
        required=False, related='offer_id.bank_id')
    offer_id = fields.Many2one(
        comodel_name='esd.offer.sale',
        string='Offer',
        required=False, domain="[('is_financing_sale', '=', is_financing_sale)]")
    document_required_ids = fields.One2many(
        comodel_name='esd.sale.document',
        inverse_name='sale_id',
        string='Document Required',
        required=False)
    will_be_pay_by_bank = fields.Boolean(
        string='Will Be Pay by Bank',
        required=False, compute='compute_will_be_pay_by_bank', store=True)
    approbation_code = fields.Char(
        string='Approbation Code',
        required=False)
    payment_filename = fields.Char(
        string='Payment Filename',
        required=False)
    payment_file = fields.Binary(string="Payment Document", )
    purchase_filename = fields.Char(
        string='Purchase Filename',
        required=False)
    purchase_file = fields.Binary(string="Purchase Order", )
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", default=1)

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):

        if not self.is_financing_sale:

            def compute_taxes(order_line):
                price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                order = order_line.order_id
                return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                             product=order_line.product_id,
                                                             partner=order.partner_shipping_id)

            account_move = self.env['account.move']
            for order in self:
                tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
                                                                                             compute_taxes)
                tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                          order.amount_untaxed, order.currency_id)
                order.tax_totals_json = json.dumps(tax_totals)
        else:
            def compute_taxes(order_line):
                if order_line.payment_plan_id:
                    price = (order_line.price_unit / order_line.payment_plan_id.qty_payment) * (1 - (order_line.discount or 0.0) / 100.0)
                    order = order_line.order_id
                    return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                                 product=order_line.product_id,
                                                                 partner=order.partner_shipping_id)
                else:
                    price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                    order = order_line.order_id
                    return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                                 product=order_line.product_id,
                                                                 partner=order.partner_shipping_id)

            account_move = self.env['account.move']
            for order in self:
                tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
                                                                                             compute_taxes)
                tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                          order.amount_untaxed, order.currency_id)
                order.tax_totals_json = json.dumps(tax_totals)


    @api.onchange('offer_id')
    def _onchange_offer_id(self):
        for line in self.order_line:
            if self.offer_id.line_ids:
                offer = self.offer_id.line_ids.filtered(lambda r: r.product_id.id == line.product_id.id)
                if line:
                    line.discount = offer[0].discount


    @api.depends('offer_id')
    def compute_will_be_pay_by_bank(self):
        for rec in self:
            if rec.offer_id.payment_by_bank:
                rec.will_be_pay_by_bank = True
            else:
                rec.will_be_pay_by_bank = False

    def check_documents(self):

        count_document = 0
        count_doc_sale = 0

        if self.partner_id.company_type == 'person':
            count_document = len(self.env['esd.type.document'].search([('is_individual', '=', True)]))
            count_doc_sale = len(self.document_required_ids.filtered(lambda r: r.name.is_individual))
        else:
            count_document = len(self.env['esd.type.document'].search([('is_company', '=', True)]))
            count_doc_sale = len(self.document_required_ids.filtered(lambda r: r.name.is_company))

        if not count_doc_sale == count_document:
            raise ValidationError(_("You must add many document for confirmation to this type of customer."))

        for document in self.document_required_ids:
            if not document.file_document:
                raise ValidationError(_("You must add many file for confirmation."))

    def _action_confirm(self):

        self.check_documents()

        if not self.document_required_ids:
            raise ValidationError(_("You must add many document for confirmation."))

        super()._action_confirm()

        if self.offer_id.payment_by_bank:
            for line in self.order_line:

                self.env['payment.bank.line'].create({
                    'product_id': line.product_id.id,
                    'currency_id': line.order_id.currency_id.id,
                    'bank_id': line.order_id.bank_id.id,
                    'bank_amount': line.bank_amount,
                    'customer_amount': line.customer_amount,
                    'sale_id': line.order_id.id,
                    'sale_line_id': line.id,
                    'company_id': line.company_id.id,
                    'approbation_code': self.approbation_code
                })

        if self.is_financing_sale:
            for line in self.order_line:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_shipping_id)

                line.fee_plan_id = self.env['esd.payment.plan.fee'].create({
                    'partner_id': self.partner_id.id,
                    'payment_plan_id': line.payment_plan_id.id,
                    'date': self.date_order,
                    'currency_id': self.pricelist_id.currency_id.id,
                    'amount_financed': taxes['total_excluded'],
                    'sale_id': self.id,
                    'sale_line_id': line.id,
                    'product_id': line.product_id.id
                })
                line.fee_plan_id.create_plan_fee()

        return True
