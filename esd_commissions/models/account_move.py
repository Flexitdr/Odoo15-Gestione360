# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class Invoice(models.Model):
    _inherit = 'account.move'
    _order = 'id desc'

    @api.model
    def create_invoice_commission(self):

        invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'), ('journal_id', 'in', [1, 9])])

        for invoice in invoices:
            invoice.create_commission()

    def create_commission(self):

        if self.payment_state in ('paid', 'partial', 'in_payment', 'reversed'):

            for payment_val in self.sudo()._get_reconciled_info_JSON_values():

                # payment_id = self.env['account.payment'].search([('id', '=', payment_val['account_payment_id'])],
                #                                                 limit=1)
                # if payment_id.date:

                commission_lines_last = self.env['commission.line'].search([('payment', '=', payment_val['ref']),
                                                                            ('invoice_id', '=', self.id)])
                if not commission_lines_last:
                    self.create_commission_own_payments(payment_val)
                    self.create_commission_own_sales_payments(payment_val)
                    self.create_commission_other_payments(payment_val)
                    self.create_commission_product_category(payment_val)

            revert = self.env['account.move'].search([('l10n_do_origin_ncf', '=', self.l10n_latam_document_number),
                                                      ('state', '=', 'posted')], limit=1)

            if revert:
                for payment_val in self.sudo()._get_reconciled_info_JSON_values():
                    average = self.amount_total_signed / self.amount_untaxed_signed

                    commission_lines_reversed = self.env['commission.line'].search([('invoice_id', '=', self.id),
                                                                                    ('is_reverse', '=', True),
                                                                                    ('payment_int_id', '=',
                                                                                     payment_val['payment_id'])])
                    if not commission_lines_reversed:
                        if not revert.id == payment_val['move_id']:
                            commission_lines_last = self.env['commission.line'].search([('payment_int_id', '=',
                                                                                         payment_val['payment_id']),
                                                                                        ('is_reverse', '=', False),
                                                                                        ('invoice_id', '=', self.id)])

                            ratio_payment_invoiced = (payment_val['amount'] / average) / self.amount_untaxed_signed

                            difference = (payment_val['amount'] / average) - (
                                    (self.amount_untaxed_signed * ratio_payment_invoiced) -
                                    (abs(revert.amount_untaxed_signed) * ratio_payment_invoiced))

                            if difference >= 0:
                                percentage = difference / (payment_val['amount'] / average)

                                for commission in commission_lines_last:
                                    commission_revert = commission.commission_amount * percentage

                                    self.env['commission.line'].create({
                                        'profile_id': commission.profile_id.id,
                                        'user_id': commission.user_id.id,
                                        'invoice_id': self.id,
                                        'payment': payment_val['ref'],
                                        'payment_int_id': payment_val['payment_id'],
                                        'partner_id': self.partner_id.id,
                                        'net_amount': self.amount_untaxed_signed,
                                        'payment_amount': difference,
                                        'percentage': percentage,
                                        'commission_amount': commission_revert * (-1),
                                        'day_count': commission.day_count,
                                        'date_payment': commission.date_payment,
                                        'date_invoice': self.invoice_date,
                                        'state': 'generated',
                                        'is_reverse': True,
                                        'commission_line_to_revert_id': commission.id
                                    })
                        else:
                            commission_lines_last = self.env['commission.line'].search([('payment_int_id', '=',
                                                                                         payment_val['payment_id']),
                                                                                        ('is_reverse', '=', False),
                                                                                        ('invoice_id', '=', self.id)])
                            for commission in commission_lines_last:
                                self.env['commission.line'].create({
                                    'profile_id': commission.profile_id.id,
                                    'user_id': commission.user_id.id,
                                    'invoice_id': self.id,
                                    'payment': payment_val['ref'],
                                    'payment_int_id': payment_val['payment_id'],
                                    'partner_id': self.partner_id.id,
                                    'net_amount': self.amount_untaxed_signed,
                                    'payment_amount': commission.payment_amount,
                                    'percentage': commission.percentage,
                                    'commission_amount': commission.commission_amount * (-1),
                                    'day_count': commission.day_count,
                                    'date_payment': commission.date_payment,
                                    'date_invoice': self.invoice_date,
                                    'state': 'generated',
                                    'is_reverse': True,
                                    'commission_line_to_revert_id': commission.id
                                })

    def create_commission_own_payments(self, payment_val):

        payment_id = self.env['account.payment'].search([('id', '=', payment_val['account_payment_id'])])

        if payment_id:

            profile_own_payments = self.env['profile.commission'].search([('type_profile', '=', 'own_payments')])

            average = self.amount_total_signed / self.amount_untaxed_signed

            payment_amount = payment_id.currency_id._convert(payment_val['amount'],
                                                             self.company_currency_id, self.company_id,
                                                             payment_id.date)

            sale_financing = self.line_ids.sale_line_ids.filtered(lambda r: r.fee_plan_id)

            # raise UserError("%s" % (profile_own_sales_payments) )

            for profile in profile_own_payments:
                if payment_id.create_uid.id in profile.user_ids.ids:
                    result = profile.calculate_commission(payment_id.date, self.invoice_date)

                    commission = (payment_amount / average) * (result['percentage'] / 100)

                    if sale_financing:
                        self.env['commission.line'].create({
                            'profile_id': profile.id,
                            'user_id': payment_id.create_uid.id,
                            'invoice_id': self.id,
                            'payment': payment_id.name,
                            'is_financing': True,
                            'payment_int_id': payment_val['payment_id'],
                            'partner_id': self.partner_id.id,
                            'net_amount': self.amount_untaxed_signed,
                            'payment_amount': payment_amount / average,
                            'percentage': result['percentage'],
                            'commission_amount': sale_financing.fee_plan_id.sale_id.amount_untaxed,
                            'day_count': result['days_count'],
                            'date_payment': payment_id.date,
                            'date_invoice': self.invoice_date,
                            'external_provider': profile.external_provider,
                            'state': 'generated'
                        })
                    else:
                        self.env['commission.line'].create({
                            'profile_id': profile.id,
                            'user_id': payment_id.create_uid.id,
                            'invoice_id': self.id,
                            'payment': payment_id.name,
                            'is_financing': True,
                            'payment_int_id': payment_val['payment_id'],
                            'partner_id': self.partner_id.id,
                            'net_amount': self.amount_untaxed_signed,
                            'payment_amount': payment_amount / average,
                            'percentage': result['percentage'],
                            'commission_amount': commission,
                            'day_count': result['days_count'],
                            'date_payment': payment_id.date,
                            'date_invoice': self.invoice_date,
                            'external_provider': profile.external_provider,
                            'state': 'generated'
                        })

    def create_commission_own_sales_payments(self, payment_id):

        profile_own_sales_payments = self.env['profile.commission'].search(
            [('type_profile', '=', 'own_sales_payments')])

        average = self.amount_total_signed / self.amount_untaxed_signed

        currency_id = self.env['res.currency'].search([('symbol', '=', payment_id['currency'])], limit=1)

        payment_amount = currency_id._convert(payment_id['amount'],
                                              self.company_currency_id, self.company_id,
                                              payment_id['date'])

        payment = self.env['account.payment'].search([('id', '=', payment_id['account_payment_id'])])

        from_reverse = False

        sale_financing = self.line_ids.sale_line_ids.filtered(lambda r: r.fee_plan_id)

        # raise UserError("%s" % (profile_own_sales_payments))

        for profile in profile_own_sales_payments:
            if self.invoice_user_id.id in profile.user_ids.ids:

                result = profile.calculate_commission(payment_id['date'], self.invoice_date)

                commission = (payment_amount / average) * (result['percentage'] / 100)

                if sale_financing:

                    self.env['commission.line'].create({
                        'profile_id': profile.id,
                        'user_id': self.invoice_user_id.id,
                        'invoice_id': self.id,
                        'is_financing': True,
                        'fee_qty': profile.commission_period_line_ids.fee_qty,
                        'payment': payment_id['ref'],
                        'payment_int_id': payment_id['payment_id'],
                        'partner_id': self.partner_id.id,
                        'net_amount': self.amount_untaxed_signed,
                        'payment_amount': payment_amount / average,
                        'percentage': result['percentage'],
                        'commission_amount': sale_financing.fee_plan_id.sale_id.amount_untaxed,
                        'day_count': result['days_count'],
                        'date_payment': payment_id['date'],
                        'date_invoice': self.invoice_date,
                        'state': 'generated',
                        'external_provider': profile.external_provider,
                        'from_reverse': from_reverse
                    })

                else:

                    self.env['commission.line'].create({
                        'profile_id': profile.id,
                        'user_id': self.invoice_user_id.id,
                        'invoice_id': self.id,
                        'payment': payment_id['ref'],
                        'payment_int_id': payment_id['payment_id'],
                        'partner_id': self.partner_id.id,
                        'net_amount': self.amount_untaxed_signed,
                        'payment_amount': payment_amount / average,
                        'percentage': result['percentage'],
                        'commission_amount': commission,
                        'day_count': result['days_count'],
                        'date_payment': payment_id['date'],
                        'date_invoice': self.invoice_date,
                        'state': 'generated',
                        'external_provider': profile.external_provider,
                        'from_reverse': from_reverse

                    })

    def create_commission_other_payments(self, payment_id):

        profile_other_payments = self.env['profile.commission'].search([('type_profile', '=', 'other_payments')])

        average = self.amount_total_signed / self.amount_untaxed_signed

        currency_id = self.env['res.currency'].search([('symbol', '=', payment_id['currency'])], limit=1)

        payment_amount = self.company_currency_id._convert(payment_id['amount'],
                                                           currency_id, self.company_id,
                                                           payment_id['date'])

        payment = self.env['account.payment'].search([('id', '=', payment_id['account_payment_id'])])

        sale_financing = self.line_ids.sale_line_ids.filtered(lambda r: r.fee_plan_id)

        from_reverse = False

        # raise UserError(str(payment_id.date) + "%s" % (payment_id.name))

        for profile in profile_other_payments:

            commission_lines = self.env['commission.line'].search([('payment_int_id', '=', payment_id['payment_id'])])

            commission_lines = commission_lines.filtered(lambda r: r.user_id.id in profile.salesperson_ids.ids)

            if commission_lines:

                for commision_line in commission_lines:
                    commision_line.manager_id = profile.user_ids[0].id

                result = profile.calculate_commission(payment_id['date'], self.invoice_date)

                commission = (payment_amount / average) * (result['percentage'] / 100)

                if sale_financing:
                    self.env['commission.line'].create({
                        'profile_id': profile.id,
                        'user_id': profile.user_ids[0].id,
                        'invoice_id': self.id,
                        'payment': payment_id['ref'],
                        'is_financing': True,
                        'fee_qty': profile.commission_period_line_ids.fee_qty,
                        'payment_int_id': payment_id['payment_id'],
                        'partner_id': self.partner_id.id,
                        'net_amount': self.amount_untaxed_signed,
                        'payment_amount': payment_amount / average,
                        'percentage': result['percentage'],
                        'commission_amount': sale_financing.fee_plan_id.sale_id.amount_untaxed,
                        'day_count': result['days_count'],
                        'date_payment': payment_id['date'],
                        'date_invoice': self.invoice_date,
                        'state': 'generated',
                        'external_provider': profile.external_provider,
                        'from_reverse': from_reverse

                    })

                else:
                    self.env['commission.line'].create({
                        'profile_id': profile.id,
                        'user_id': profile.user_ids[0].id,
                        'invoice_id': self.id,
                        'payment': payment_id['ref'],
                        'payment_int_id': payment_id['payment_id'],
                        'partner_id': self.partner_id.id,
                        'net_amount': self.amount_untaxed_signed,
                        'payment_amount': payment_amount / average,
                        'percentage': result['percentage'],
                        'commission_amount': commission,
                        'day_count': result['days_count'],
                        'date_payment': payment_id['date'],
                        'date_invoice': self.invoice_date,
                        'state': 'generated',
                        'external_provider': profile.external_provider,
                        'from_reverse': from_reverse

                    })

    def create_commission_product_category(self, payment_id):

        profile_product_category = self.env['profile.commission'].search([('type_profile', '=', 'product_category')])

        average = self.amount_total_signed / self.amount_untaxed_signed
        currency_id = self.env['res.currency'].search([('symbol', '=', payment_id['currency'])], limit=1)

        payment_amount = currency_id._convert(payment_id['amount'],
                                              self.company_currency_id, self.company_id,
                                              payment_id['date'])

        payment = self.env['account.payment'].search([('id', '=', payment_id['account_payment_id'])])

        sale_financing = self.line_ids.sale_line_ids.filtered(lambda r: r.fee_plan_id)

        from_reverse = False

        # raise UserError("%s" % (profile_own_sales_payments) )

        for profile in profile_product_category:

            for user in profile.user_ids:

                if profile.for_own_sales:
                    if not self.invoice_user_id.id == user.id:
                        continue

                invoice_lines = self.invoice_line_ids.filtered(
                    lambda r: r.product_id.categ_id.id in profile.product_category_ids.ids)

                if invoice_lines:
                    result = profile.calculate_commission(payment_id['date'], self.invoice_date)

                    total = 0.0

                    for line in invoice_lines:
                        total += line.price_subtotal

                    total_currency = self.currency_id._convert(total,
                                                               self.company_currency_id, self.company_id,
                                                               self.invoice_date)

                    commission_by_line = total_currency * (result['percentage'] / 100)

                    payment_untaxed = payment_amount / average

                    percentage_payment = payment_untaxed / self.amount_untaxed_signed

                    commission = commission_by_line * percentage_payment

                    if sale_financing:
                        self.env['commission.line'].create({
                            'profile_id': profile.id,
                            'user_id': user.id,
                            'invoice_id': self.id,
                            'payment': payment_id['ref'],
                            'is_financing': True,
                            'fee_qty': profile.commission_period_line_ids.fee_qty,
                            'payment_int_id': payment_id['payment_id'],
                            'partner_id': self.partner_id.id,
                            'net_amount': self.amount_untaxed_signed,
                            'payment_amount': payment_amount / average,
                            'percentage': result['percentage'],
                            'commission_amount': sale_financing.fee_plan_id.sale_id.amount_untaxed,
                            'day_count': result['days_count'],
                            'date_payment': payment_id['date'],
                            'date_invoice': self.invoice_date,
                            'state': 'generated',
                            'external_provider': profile.external_provider,
                            'from_reverse': from_reverse
                        })

                    else:
                        self.env['commission.line'].create({
                            'profile_id': profile.id,
                            'user_id': user.id,
                            'invoice_id': self.id,
                            'payment': payment_id['ref'],
                            'payment_int_id': payment_id['payment_id'],
                            'partner_id': self.partner_id.id,
                            'net_amount': self.amount_untaxed_signed,
                            'payment_amount': payment_amount / average,
                            'percentage': result['percentage'],
                            'commission_amount': commission,
                            'day_count': result['days_count'],
                            'date_payment': payment_id['date'],
                            'date_invoice': self.invoice_date,
                            'state': 'generated',
                            'external_provider': profile.external_provider,
                            'from_reverse': from_reverse
                        })
