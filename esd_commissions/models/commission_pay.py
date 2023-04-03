# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class CommissionPay(models.Model):
    _name = 'commission.pay.form'
    _description = 'Commission Pay'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection(string='State', selection=[('draft', 'Draft'),
                                                        ('generated', 'Generated'),
                                                        ('validated', 'Validated'),
                                                        ('paid', 'Paid'),
                                                        ('cancel', 'Cancelled')], required=False, default='draft')
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    commission_line_ids = fields.One2many(comodel_name='commission.line', inverse_name='commission_pay_form_id',
                                          string='Commission Line', required=False)
    external_provider = fields.Boolean(string='External Provider')
    company_id = fields.Many2one(comodel_name='res.company', string='Company_id', required=False, default=lambda self: self.env.user.company_id.id)
    commission_count = fields.Float(compute='_compute_commission_count', string='Commissions')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',
                                  required=False, default=lambda self: self.env.user.company_id.currency_id.id)
    amount_total = fields.Float(string='Amount Total', required=False, compute="_compute_amounts")
    amount_commission = fields.Float(string='Amount Commission', required=False, compute="_compute_amounts")
    amount_revert = fields.Float(string='Amount Revert', required=False, compute="_compute_amounts")

    @api.depends('commission_line_ids')
    def _compute_amounts(self):

        for rec in self:

            commission_lines = rec.commission_line_ids.filtered(lambda r: not r.is_reverse)
            revert_lines = rec.commission_line_ids.filtered(lambda r: r.is_reverse)

            total_commission = 0.0
            total_revert = 0.0

            for commission in commission_lines:
                total_commission += commission.commission_amount

            for revert in revert_lines:
                total_revert += revert.commission_amount

            rec.amount_commission = total_commission
            rec.amount_revert = total_revert
            rec.amount_total = total_commission - (total_revert * (-1))

    @api.depends('commission_line_ids')
    def _compute_commission_count(self):

        for rec in self:
            rec.commission_count = len(rec.commission_line_ids)

    def action_view_commissions(self):

        action = self.env["ir.actions.actions"]._for_xml_id("esd_commissions.manager_commission_line_action")
        action['domain'] = [('commission_pay_form_id', '=', self.id)]
        action['context'] = {
            'commission_pay_form_id': self.id,
        }

        return action

    def load_commission(self):
        commission_lines = self.env['commission.line'].search([('company_id', '=', self.company_id.id),
                                                               ('date', '>=', self.from_date), ('date', '<=', self.to_date),
                                                               ('state', 'in', ('generated', 'partial')),
                                                               ('external_provider', '=', self.external_provider)])
        for commission in commission_lines:

            if commission.is_financing and commission.fee_qty > 0:
                commission.commission_pay_form_id = self.id
                fee_qty_updated = int(commission.fee_qty) - 1

                values = {
                    'fee_qty': fee_qty_updated,
                    'state': 'partial'

                }

                commission.write(values)
            else:
                commission.commission_pay_form_id = self.id

            self.state = 'generated'

    def validate_this(self):

        for commission in self.commission_line_ids:
            commission.state = 'validated'

        self.state = 'validated'

    def paid_this(self):

        for commission in self.commission_line_ids:

            if commission.is_financing and commission.fee_qty > 0:
                commission.commission_pay_form_id = self.id

                values = {
                    'state': 'partial'

                }

                commission.write(values)
            else:
                commission.commission_pay_form_id = self.id

                self.state = 'paid'

    def cancel_action(self):
        for commission in self.commission_line_ids:
            commission.state = 'cancel'
        self.state = 'cancel'

    def _create_invoice(self, partner, commissions):

        invoice_line = []

        product_commission = self.env['product.product'].search([('is_commission', '=', True)], limit=1)

        for commission in commissions:

            invoice_line.append((0, 0, {
                'name': self.name + ':' + commission.invoice_id.name,
                'price_unit': commission.commission_amount,
                'product_id': product_commission.id,
                'tax_ids': [],

            }))

        journal = self.env['account.journal'].search([('commission_pay', '=', True)], limit=1)

        self.env['account.move'].create(
            {
                'move_type': 'in_invoice',
                'date': fields.Date.today(),
                'invoice_date': fields.Date.today(),
                'partner_id': partner.id,
                'currency_id': partner.currency_id.id,
                'invoice_line_ids': invoice_line,
                'journal_id': journal.id,
            })

    def create_invoice(self):

        profiles = self.env['profile.commission'].search([('external_provider', '=',  True)])

        for profile in profiles:

            for user in profile.user_ids:

                commissions = self.commission_line_ids.filtered(lambda r: r.user_id == user)

                self._create_invoice(user.partner_id, commissions)

    def commissions_reports(self):

        report = self.env.ref('esd_commissions.action_commission_report')._render_qweb_pdf(self.id)

    def commissions_reports_by_user(self):

        report = self.env.ref('esd_commissions.action_commission_report_by_user')._render_qweb_pdf(self.id)
