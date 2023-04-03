# -*- coding: utf-8 -*-
###############################################################################
#
#   seller_website_live_helpdesk for Odoo
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import re

# Since invoice amounts are unsigned, this is how we know if money comes in or goes out

class account_register_payments(models.TransientModel):
    _inherit = "account.payment.register"

    invoices_id = fields.One2many('register.payment.line', 'register_payment_id', string="Invoices")
    memo=fields.Char(string="Memo",invisible="1")
    
    @api.model
    def default_get(self, fields):
        rec = super(account_register_payments, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        invoices = self.env['account.move'].browse(active_ids)
        if not active_ids:
            raise UserError(_("Programming error: wizard action executed without active_ids in context."))
        if active_model != 'account.move':
            raise UserError(_("Programmation error: the expected model for this action is 'account.move'. The provided one is '%d'.") % active_model)

        invoice_lines = []
        for invoice in invoices:
            invoice_vals = {
                'register_payment_id': self.id,
                'invoice_id': invoice.id,
                'dup_invoice_id': invoice.id,
                'partner_id': invoice.partner_id.id,
                'dup_partner_id': invoice.partner_id.id,
                'description': invoice.name,
                'invoice_amount': invoice.amount_total,
                'residual_amount': abs(invoice.amount_residual_signed),
                'amount_to_pay':abs(invoice.amount_residual_signed)
            }
            invoice_lines.append((0, 0, invoice_vals))
        rec.update({
            'invoices_id': invoice_lines
        })

       
        return rec


    @api.onchange('invoices_id')
    def _onchange_invoices_id(self):
        sum = 0.0
        for i in self.invoices_id:
            if i.dup_partner_id :
                sum += i.amount_to_pay
                self.amount = sum
           

    def _create_payment_vals_from_wizard(self):
        active_ids = self._context.get('active_ids')
        records = self.env['account.move'].browse(active_ids)
        payment_vals={}
        
        for av in records:
            payment_vals = {
                'date': av.payment_date if av.payment_date else self.payment_date,
                'amount': self.amount,
                'payment_type': self.payment_type,
                'partner_type': self.partner_type,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
                'partner_bank_id': self.partner_bank_id.id,
                'destination_account_id': self.line_ids[0].account_id.id
            }
            if self.payment_difference and self.payment_difference_handling == 'reconcile':
                payment_vals['write_off_line_vals'] = {
                    'name': self.writeoff_label,
                    'amount': self.payment_difference,
                    'account_id': self.writeoff_account_id.id,
                }
        return payment_vals

   
    def _create_payment_vals_from_batch(self, batch_result):
        rec = super(account_register_payments, self)._create_payment_vals_from_batch(batch_result)
        for date in self.invoices_id:
            
            if date.dup_invoice_id.partner_id.id == rec['partner_id']:
                if date.dup_invoice_id.payment_date:
                    rec['date'] = date.dup_invoice_id.payment_date
                else:
                    rec['date'] = self.payment_date
         
        if not self.group_payment:
            for line in self.invoices_id:
                if line.dup_invoice_id and rec.get('ref'):
                    if line.dup_invoice_id and line.dup_invoice_id.name == rec['ref']:
                        rec['amount'] = line.amount_to_pay
        else:
            sum = 0.0
            found = False
            for i in self.invoices_id:
                if i.dup_partner_id.id == rec.get('partner_id'):
                    sum += i.amount_to_pay
                    found = True
            if found:
                rec['amount'] = sum

    
        return rec    
       



            

    def create_payment(self):
        payments = self._create_payments()
        for i in payments:
            if i.ref.split('/')[0] == 'BILL':
                for inv in i.reconciled_bill_ids:
                    if inv.amount_residual == 0.0 and inv.is_called == False:
                        if inv.payment_date:
                            i.date = inv.payment_date
                        else:
                            i.date = self.payment_date

                            av=inv.invoice_payments_widget
                            data = json.loads(av)
                            res = data.get('content')[-1].get('date')
                            if inv.amount_residual == 0.0:
                                if inv.payment_date == False:
                                    inv.payment_date = res
                    elif inv.amount_residual != 0.0 and inv.is_called == False:
                        if inv.payment_date:
                            i.date = inv.payment_date
                        else:
                            i.date = self.payment_date
                        inv.is_called = True
                    else:
                        i.date = self.payment_date
                        if inv.amount_residual == 0.0:
                            inv.payment_date = self.payment_date
                
            else:
                for inv in i.reconciled_invoice_ids:
                    if inv.amount_residual == 0.0 and inv.is_called == False:
                        if inv.payment_date:
                            i.date = inv.payment_date
                        else:
                            i.date = self.payment_date

                            av=inv.invoice_payments_widget
                            data = json.loads(av)
                            res = data.get('content')[-1].get('date')
                            if inv.amount_residual == 0.0:
                                if inv.payment_date == False:
                                    inv.payment_date = res
                    elif inv.amount_residual != 0.0 and inv.is_called == False:
                        if inv.payment_date:
                            i.date = inv.payment_date
                        else:
                            i.date = self.payment_date
                        inv.is_called = True
                    else:
                        i.date = self.payment_date
                        if inv.amount_residual == 0.0:
                            inv.payment_date = self.payment_date
                                   

            for invoice_line in self.invoices_id:
                if invoice_line.invoice_id in i.reconciled_invoice_ids:
                    if self.group_payment:
                        pass
                    else:
                        i.amount = invoice_line.amount_to_pay

        if self._context.get('dont_redirect_to_payments'):
            return True
        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payments.ids)],
        }

        return action

class RegisterPaymentLine(models.TransientModel):
    _name = "register.payment.line"
    _description = "Payment Invoice Lines"

    register_payment_id = fields.Many2one('account.payment.register', 'Register Payment')
    invoice_id = fields.Many2one('account.move', 'Invoice')
    dup_invoice_id = fields.Many2one('account.move', 'Invoice',store=True)
    partner_id = fields.Many2one('res.partner', string="Client")
    dup_partner_id = fields.Many2one('res.partner', string="Client",store=True)
    description = fields.Char('Description')
    invoice_amount = fields.Float('Invoice Amount')
    dup_invoice_amount = fields.Float('Invoice Amount')
    residual_amount = fields.Float('Residual Amount')
    dup_residual_amount = fields.Float('Residual Amount')
    amount_to_pay = fields.Float('Payment Amount')
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', store=True)
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', store=True)
    
