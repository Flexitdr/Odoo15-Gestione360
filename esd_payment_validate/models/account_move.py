# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError
from ..controllers.payment_validate import read_azul_transaction
from datetime import date


class AccountMove(models.Model):
    _inherit = 'account.move'

    def validate_payment(self):

        invoices = self.search([('state', '=', 'posted'),
                                ('payment_state', 'in', ('not_paid', 'partial'))])

        azul_validate = read_azul_transaction()

        dict_list = []

        dict_client = {}

        list_client = []

        for invoice in invoices:

            paid_client = sum(
                float(x['Amount'].replace(',', '')) for x in azul_validate if x['IdentNum'] == invoice.partner_id.vat)

            for azul in azul_validate:

                if invoice.partner_id.vat == azul['IdentNum']:

                    if not invoice.partner_id.vat in list_client:

                        list_client.append(invoice.partner_id.vat)

                        if invoice.payment_state == 'not_paid':

                            amount_to_pay = paid_client - invoice.amount_total

                            total_amount = paid_client - amount_to_pay

                            if invoices.search_count([('partner_id', '=', invoice.partner_id.id)]) == 1:
                                self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                  active_ids=invoice.ids) \
                                    .create({'amount': paid_client,
                                             'payment_date': date.today()}) \
                                    ._create_payments()

                                self.env['account.move.line'].change_subs_state(invoice)

                            else:
                                self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                  active_ids=invoice.ids) \
                                    .create({'amount': total_amount,
                                             'payment_date': date.today()}) \
                                    ._create_payments()

                                dict_client = {**dict_client, 'client': invoice.partner_id.vat, 'amount': amount_to_pay}

                                dict_list.append(dict_client)

                                self.env['account.move.line'].change_subs_state(invoice)

                        if invoice.payment_state == 'partial':

                            amount_to_pay = paid_client - invoice.amount_total

                            total_amount = paid_client - amount_to_pay

                            if invoices.search_count([('partner_id', '=', invoice.partner_id.id)]) == 1:
                                self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                  active_ids=invoice.ids) \
                                    .create({'amount': paid_client,
                                             'payment_date': date.today()}) \
                                    ._create_payments()

                                self.env['account.move.line'].change_subs_state(invoice)

                            else:
                                self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                  active_ids=invoice.ids) \
                                    .create({'amount': total_amount,
                                             'payment_date': date.today()}) \
                                    ._create_payments()

                                dict_client = {**dict_client, 'client': invoice.partner_id.vat, 'amount': amount_to_pay}

                                self.env['account.move.line'].change_subs_state(invoice)

                    if invoice.partner_id.vat in list_client:

                        for client in dict_list:

                            if invoice.payment_state == 'not_paid':

                                if client['client'] == invoice.partner_id.vat:

                                    if client['amount'] > 0:

                                        self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                              active_ids=invoice.ids)\
                                            .create({'amount': abs(client['amount']), 'payment_date': date.today()})._create_payments()

                                        self.env['account.move.line'].change_subs_state(invoice)

                            if invoice.payment_state == 'partial':

                                if client['client'] == invoice.partner_id.vat:

                                    if client['amount'] > 0:

                                        self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                          active_ids=invoice.ids) \
                                            .create({'amount': abs(client['amount']),
                                                     'payment_date': date.today()}) \
                                            ._create_payments()

                                        self.env['account.move.line'].change_subs_state(invoice)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def change_subs_state(self, vals):

        subs_line = self.env['subscription.payment.line'].search([('state', '=', 'generated')])

        for subs in subs_line:

            for val in vals['invoice_line_ids']:

                if subs.invoice_code == val.name:
                    subs.state = 'paid'
