# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    fee_id = fields.Char()
    equipment_id = fields.Many2one('esd.services.equipment', string='Equipment', readonly=True)
    plan_id = fields.Many2one('subscription.package', string='Plan', readonly=True)
    duration = fields.Date(string='Duration', readonly=True)


class AccountMove(models.Model):

    _inherit = 'account.move'

    is_recurrence = fields.Boolean(string='Is recurrence', default=False)

    @api.model
    def create_invoices_and_fee(self):

        a = 0

        subs = self.env['subscription.payment.line'].search([('state', '=', 'created')], limit=200)

        itbis = self.env.company.account_sale_tax_id

        recurrence = self.env.ref('esd_recurrence_and_fee.esd_product_recurrence')

        for partner in subs.partner_id:
            subs_ids = subs.filtered(lambda r: r.partner_id.id == partner.id)

            fee = self.env['esd.payment.plan.fee'].search([('state', '=', 'running'), ('partner_id', '=', partner.id)])

            lines = []

            for line_subs in subs_ids:

                lines.append((0, 0, {
                    'name': line_subs.invoice_code,
                    'price_unit': line_subs.recurring_price,
                    'product_id': recurrence.id,
                    'equipment_id': line_subs.equipment,
                    'fee_id': line_subs.qty_fee,
                    'duration': line_subs.plan_duration,
                    'tax_ids': itbis,

                }))

                line_subs.state = 'generated'

                print('s {}'.format(a))
                a += 1
                continue

            for line_fee in fee.fee_ids:

                if line_fee.payment_date == date.today():

                    lines.append((0, 0, {
                        'name': line_fee.sale_id.name,
                        'price_unit': line_fee.amount_to_pay,
                        'product_id': recurrence.id,
                        'fee_id': line_fee.qty_fee,
                        'tax_ids': itbis,

                    }))

                    line_fee.state = 'generated'

            self.env['account.move'].create(
                {
                    'move_type': 'out_invoice',
                    'date': fields.Date.today(),
                    'invoice_date': fields.Date.today(),
                    'partner_id': partner.id,
                    'is_recurrence': True,
                    'currency_id': partner.currency_id.id,
                    'invoice_line_ids': lines,
                    'journal_id': 1,
                })

