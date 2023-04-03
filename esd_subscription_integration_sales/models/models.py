# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError
import json
import logging
from datetime import timedelta
from collections import defaultdict
from datetime import datetime


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    subscription_plane_id = fields.Many2one(
        comodel_name='subscription.package.plan',
        string='Subscription Plane',
        domain="[('limit_count', '<=', 12)]",
        required=False)
    subscription_package_id = fields.Many2one(
        comodel_name='subscription.package',
        string='Subscription Package',
        required=False)

    payment_format = fields.Selection([
        ('1', '1 Month'),
        ('3', '3 Month'),
        ('6', '6 Month'),
        ('12', '1 Year')], default='1')

    subs_lines = fields.Boolean(default=False)

    @api.onchange('subscription_plane_id')
    def _onchange_subscription_plane_id(self):

        if self.subscription_plane_id.limit_count >= 12:
            self.type_subscription = 'subscription'
        else:
            self.type_subscription = 'visit'

    @api.onchange('financing_id')
    def onchange_subscription_plan(self):

        if self.financing_id.qty_month == 48:

            subs = self.subscription_plane_id.search([('limit_count', '=', 48)])

            self.subscription_plane_id = subs

        if self.financing_id.qty_month == 36:

            subs = self.subscription_plane_id.search([('limit_count', '=', 36)])

            self.subscription_plane_id = subs

        if self.financing_id.qty_month == 24:

            subs = self.subscription_plane_id.search([('limit_count', '=', 24)])

            self.subscription_plane_id = subs

        if self.financing_id.qty_month == 12:

            subs = self.subscription_plane_id.search([('limit_count', '=', 12)])

            self.subscription_plane_id = subs

        if not self.financing_id and self.type_subscription == 'subscription':
            subs = self.subscription_plane_id.search([('limit_count', '=', 12)])

            self.subscription_plane_id = subs

    def create_subscription(self):

        product_plan = self.env['product.product'].search([('id', '=', self.product_id.id)], limit=1)

        sale_id = self.env['sale.order'].search([('order_line', '=', self.id)])

        subscription = self.subscription_package_id = self.env['subscription.package'].create({
            'partner_id': self.order_id.partner_id.id,
            'plan_id': self.subscription_plane_id.id,
            'payment_format': self.payment_format,
            'sale_id': sale_id.id,
            'product_line_ids': [(0,0, {
                'product_id': product_plan.subscription_plan_product_id.id,
                'product_qty': int(self.payment_format),
                'unit_price': product_plan.subscription_plan_product_id.lst_price,
                'total_amount': product_plan.subscription_plan_product_id.lst_price
            })]
        })

        return subscription

    def create_visit_maintenance(self):

        product_plan = self.env['product.product'].search([('id', '=', self.product_id.id)], limit=1)

        sale_id = self.env['sale.order'].search([('order_line', '=', self.id)])

        subscription_visit = self.env['visit.subscription'].create({
            'partner_id': self.order_id.partner_id.id,
            'price': product_plan.visit_plan_product_id.lst_price,
            'sale_id': sale_id.id,
            'date': datetime.today(),
            'product_id': product_plan.id
        })

        return subscription_visit

    def create_installation(self):
        if not self.address_id.id:
            raise UserError("You must add any Address to this installation.")

        if self.type_subscription == 'subscription':

            subscription = self.create_subscription()
            metric_id = self.env['esd.metric.equipment'].search([('product_id', '=', self.product_id.id)], limit=1)

            equipment = self.env['esd.services.equipment'].create(
                {
                    'partner_id': self.order_partner_id.id,
                    'address_id': self.address_id.id,
                    'product_id': self.product_id.id,
                    'type_subscription': self.type_subscription,
                    'metrics_id': metric_id.id,
                    'subscription_package_id': subscription.id,
                    'sale_id': self.order_id.id
                }
            )

            subscription.equipment_id = equipment.id
            subscription.reference_code = self.env['ir.sequence'].next_by_code('sequence.reference.code') or 'New'

            tasks = self.env['esd.task.setting'].search([('product_id', '=', self.product_id.id),
                                                         ('type_task', '=', 'installation'), ])

            tasks_ids = []

            for task in tasks.task_ids:
                tasks_ids.append((0, 0, {
                    'task_id': task.id,
                    'hours': task.hours
                }))

            equipment.create_lifespan()

            metrics = []

            for metric in metric_id.metric_line_ids:
                metrics.append((0, 0, {
                    'name': metric.name,
                    'uom': metric.uom.id,
                    'equipment_id': equipment.id,
                    'metric_id': metric.id
                }))

            materials = []

            # raise UserError('\n\n\sdfasfsaf:{}'.format(self.product_id.id_installation_component))

            for material in self.product_id.installation_material_ids:
                materials.append((0, 0, {
                    'name': material.material_id.id,
                    'unit_id': material.unit_id.id,
                    'qty': material.qty
                }))

            additional_installation = []

            sale_lines = self.search([('group_id', '=', self.group_id), ('id', '!=', self.id),
                                      ('order_id', '=', self.order_id.id), ('product_id.detailed_type', '!=', 'service')])

            for sale_line in sale_lines:
                if not self.id == sale_line.id:
                    additional_installation.append((0, 0, {
                        'product_id': sale_line.product_id.id,
                        'equipment_id': equipment.id
                    }))

            installation = self.env['esd.service.installation'].create({
                'equipment_id': equipment.id,
                'request_date': datetime.today(),
                'sale_id': self.order_id.id,
                'checkmetrics_ids': metrics,
                'task_ids': tasks_ids,
                'material_ids': materials,
                'additional_installation_ids': additional_installation,
            })
        else:

            subscription_visit = self.create_visit_maintenance()
            metric_id = self.env['esd.metric.equipment'].search([('product_id', '=', self.product_id.id)], limit=1)

            equipment = self.env['esd.services.equipment'].create(
                {
                    'partner_id': self.order_partner_id.id,
                    'address_id': self.address_id.id,
                    'product_id': self.product_id.id,
                    'type_subscription': self.type_subscription,
                    'metrics_id': metric_id.id,
                    'visit_maintenance_id': subscription_visit.id,
                    'sale_id': self.order_id.id
                }
            )

            subscription_visit.equipment_id = equipment.id

            tasks = self.env['esd.task.setting'].search([('product_id', '=', self.product_id.id),
                                                         ('type_task', '=', 'installation'), ])

            tasks_ids = []

            for task in tasks.task_ids:
                tasks_ids.append((0, 0, {
                    'task_id': task.id,
                    'hours': task.hours
                }))

            equipment.create_lifespan()

            metrics = []

            for metric in metric_id.metric_line_ids:
                metrics.append((0, 0, {
                    'name': metric.name,
                    'uom': metric.uom.id,
                    'equipment_id': equipment.id,
                    'metric_id': metric.id
                }))

            materials = []

            # raise UserError('\n\n\sdfasfsaf:{}'.format(self.product_id.id_installation_component))

            for material in self.product_id.installation_material_ids:
                materials.append((0, 0, {
                    'name': material.material_id.id,
                    'unit_id': material.unit_id.id,
                    'qty': material.qty
                }))

            additional_installation = []

            sale_lines = self.search([('group_id', '=', self.group_id), ('id', '!=', self.id),
                                      ('order_id', '=', self.order_id.id),
                                      ('product_id.detailed_type', '!=', 'service')])

            for sale_line in sale_lines:
                if not self.id == sale_line.id:
                    additional_installation.append((0, 0, {
                        'product_id': sale_line.product_id.id,
                        'equipment_id': equipment.id
                    }))

            installation = self.env['esd.service.installation'].create({
                'equipment_id': equipment.id,
                'request_date': datetime.today(),
                'sale_id': self.order_id.id,
                'checkmetrics_ids': metrics,
                'task_ids': tasks_ids,
                'material_ids': materials,
                'additional_installation_ids': additional_installation,
            })

    @api.model_create_multi
    def create(self, values):

        lines = super(SaleOrderLine, self).create(values)

        for vals in values:

            if not vals['subs_lines']:
                for line in lines:

                    if line.installation_required:

                        if vals['payment_plan_id']:

                            line_product = self.env['product.product'].search([('id', '=', line.product_id.id)], limit=1)

                            price_subs = line_product.subscription_plan_product_id.lst_price * int(vals['payment_format'])

                            tax_subs = (price_subs * 0.18) + price_subs

                            if vals['type_subscription'] == 'subscription':
                                line.create({
                                    'order_id': vals['order_id'],
                                    'group_id': line.group_id,
                                    'product_id': line_product.subscription_plan_product_id.id,
                                    'name': line_product.subscription_plan_product_id.name,
                                    'product_type_related':line_product.subscription_plan_product_id.detailed_type,
                                    'product_uom_qty': 1,
                                    'price_unit': price_subs,
                                    'price_subtotal': price_subs,
                                    'subs_lines': True,
                                    'payment_format': vals['payment_format'],
                                    'subscription_plane_id': vals['subscription_plane_id']

                                })

                            else:
                                line.create({
                                    'order_id': vals['order_id'],
                                    'group_id': line.group_id,
                                    'product_id': line_product.visit_plan_product_id.id,
                                    'name': line_product.visit_plan_product_id.name,
                                    'product_type_related': line_product.visit_plan_product_id.detailed_type,
                                    'product_uom_qty': 1,
                                    'price_unit': price_subs,
                                    'price_subtotal': price_subs,
                                    'subs_lines': True,
                                    'payment_format': vals['payment_format'],
                                    'subscription_plane_id': vals['subscription_plane_id']

                                })

                return lines


class Equipment(models.Model):
    _inherit = 'esd.services.equipment'

    subscription_package_id = fields.Many2one(
        comodel_name='subscription.package',
        string='Subscription Package',
        required=False)

    visit_maintenance_id = fields.Many2one(
        comodel_name='visit.subscription',
        string='Visit Subscription',
        required=False)


class Installation(models.Model):
    _inherit = 'esd.service.installation'

    def validate(self):
        super(Installation, self).validate()

        self.equipment_id.subscription_package_id.button_start_date()

