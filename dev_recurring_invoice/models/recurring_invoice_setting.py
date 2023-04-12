# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class RecurringInvoiceSetting(models.Model):
    _name = 'recurring.invoice.setting'
    _description = 'Configuration for Recurring Invoice'

    def set_next_execution_date(self, base_date):
        if self.interval_type == 'hours':
            next_execution_date = base_date + relativedelta(hours=+self.interval_number)
        elif self.interval_type == 'days':
            next_execution_date = base_date + relativedelta(days=+self.interval_number)
        elif self.interval_type == 'weeks':
            next_execution_date = base_date + relativedelta(weeks=+self.interval_number)
        elif self.interval_type == 'months':
            next_execution_date = base_date + relativedelta(months=+self.interval_number)
        elif self.interval_type == 'years':
            next_execution_date = base_date + relativedelta(years=+self.interval_number)
        self.next_execution_date = next_execution_date

    def create_recurring_invoice(self):
        data = []
        for product_line in self.product_line_ids:
#<<<<<<< HEAD
#             data.append((0, 0, {'product_id': product_line.product_id and product_line.product_id.id or False,
#                                 'product_uom_id': product_line.uom_id and product_line.uom_id.id or False,
#                                 'name': product_line.description,
#                                 'price_unit': product_line.price,
#                                 'quantity': product_line.quantity,
#                                 'account_id': product_line.account_id and product_line.account_id.id or False,
#                                 'tax_ids': [(6, 0, product_line.tax_ids.ids)],
# #                                'sale_line_ids': [(4, product_line.sale_line_id and product_line.sale_line_id.id)],
#                                 'analytic_account_id':product_line.analytic_account_id and product_line.analytic_account_id.id,
#                                 'analytic_tag_ids':[(6, 0, product_line.analytic_tag_ids.ids)],
#                                 }))
#=======
            data_dict = {'product_id': product_line.product_id and product_line.product_id.id or False,
                         'product_uom_id': product_line.uom_id and product_line.uom_id.id or False,
                         'name': product_line.description,
                         'price_unit': product_line.price,
                         'quantity': product_line.quantity,
                         'account_id': product_line.account_id and product_line.account_id.id or False,
                         'tax_ids': [(6, 0, product_line.tax_ids.ids)],
                         'analytic_account_id': product_line.analytic_account_id and product_line.analytic_account_id.id,
                         'analytic_tag_ids': [(6, 0, product_line.analytic_tag_ids.ids)]}
            if product_line.sale_line_id:
                data_dict.update({'sale_line_ids': [(4, product_line.sale_line_id.id)]})
            data.append((0, 0, data_dict))
#>>>>>>> ef69d24e5ca8f26544b60864fa8af7912d7b5341
        new_invoice_id = self.env['account.move'].create({'partner_id': self.invoice_id.partner_id.id,
                                                          'move_type': 'out_invoice',
                                                          'invoice_line_ids': data,
                                                          'currency_id': self.invoice_id.currency_id and self.invoice_id.currency_id.id or False,
                                                          })
        if new_invoice_id:
            new_invoice_id._onchange_invoice_line_ids()
        recurred_invoices = self.recurred_invoice_ids.ids
        recurred_invoices.append(new_invoice_id.id)
        self.recurred_invoice_ids = [(6, 0, recurred_invoices)]
        if new_invoice_id.invoice_line_ids:
            all_mail = ''
            template_id = self.env.ref('dev_recurring_invoice.email_template_recurring_invoice')
            if self.notification_user_id and self.notification_user_id.partner_id and self.notification_user_id.partner_id.email:
                all_mail = self.notification_user_id.partner_id.email+','
            if self.partner_id.email:
                all_mail += self.partner_id.email
            if all_mail:
                template_id.email_to = all_mail
                template_id.send_mail(self.id, force_send=True)
                

    def process_recurring_request(self):
        if self.interval_number <= 0:
            raise ValidationError(_('''Execute Every must be positive'''))
        self.write({'state': 'processed'})
        self.set_next_execution_date(self.create_date.date())

    def set_to_new(self):
        self.write({'state': 'new'})

    def get_reoccurred_invoice_url(self):
        invoice_lst = self.recurred_invoice_ids.ids
        latest_invoice = max(invoice_lst)
        ir_param = self.env['ir.config_parameter'].sudo()
        base_url = ir_param.get_param('web.base.url')
        action_id = self.env.ref('account.action_move_out_invoice_type').id
        menu_id = self.env.ref('account.menu_finance').id
        if base_url:
            base_url += \
                '/web?#id=%s&action=%s&model=%s&view_type=form&menu_id=%s' \
                % (int(latest_invoice), action_id, 'account.move', menu_id)
        return base_url

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        if self.invoice_id:
            if self.invoice_id.partner_id:
                self.partner_id = self.invoice_id.partner_id.id
            if self.invoice_id.invoice_line_ids:
                data = []
                for line in self.invoice_id.invoice_line_ids:
                    data.append((0, 0, {'product_id': line.product_id and line.product_id.id or False,
                                        'uom_id': line.product_uom_id and line.product_uom_id.id or False,
                                        'description': line.name or '',
                                        'price': line.price_unit,
                                        'quantity': line.quantity,
                                        'sale_line_id': line.sale_line_ids,
                                        'analytic_account_id':line.analytic_account_id and line.analytic_account_id.id or False,
                                        'account_id': line.account_id and line.account_id.id or False,
                                        'analytic_tag_ids':[(6, 0, line.analytic_tag_ids.ids)],
                                        'tax_ids': [(6, 0, line.tax_ids.ids)],
                            
                                        }))
                self.product_line_ids = [(6, 0, [])]
                self.product_line_ids = data

    def cron_action_recurring_invoice(self):
        valid_recurring_ids = self.env['recurring.invoice.setting'].search([('state', '=', 'processed'),
                                                                            ('next_execution_date', '!=', False)])
        if valid_recurring_ids:
            for valid_recurring_id in valid_recurring_ids:
                if valid_recurring_id.next_execution_date:
                    next_date = valid_recurring_id.next_execution_date
                    if valid_recurring_id.stop_date:
                        stop_date = valid_recurring_id.stop_date
                        if stop_date != date.today():
#                            if next_date == date.today():
                            valid_recurring_id.create_recurring_invoice()
                            valid_recurring_id.set_next_execution_date(valid_recurring_id.next_execution_date)
                    else:
                        if next_date == date.today():
                            valid_recurring_id.create_recurring_invoice()
                            valid_recurring_id.set_next_execution_date(valid_recurring_id.next_execution_date)

    def view_recurring_invoices(self):
        tree_id = self.env.ref('account.view_invoice_tree').id
        form_id = self.env.ref('account.view_move_form').id
        if len(self.recurred_invoice_ids.ids) == 1:
            return {
                'name': 'Recurred Invoices',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'views': [(form_id, 'form')],
                'target': 'current',
                'res_id': int(self.recurred_invoice_ids.ids[0])
            }
        if len(self.recurred_invoice_ids.ids) > 1:
            return {
                'name': 'Recurred Invoices',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree, form',
                'res_model': 'account.move',
                'views': [(tree_id, 'tree'),
                          (form_id, 'form')],
                'target': 'current',
                'domain': [('id', 'in', self.recurred_invoice_ids.ids)]
            }

    def _get_recurred_invoices(self):
        for record in self:
            record.recurred_invoices = len(record.recurred_invoice_ids.ids)

    name = fields.Char(string='Name', required=True)
    state = fields.Selection(selection=[('new', 'New'),
                                        ('processed', 'Processed')], default='new', string='State')
    invoice_id = fields.Many2one('account.move', domain=[('state', '!=', 'cancel'), ('move_type', '=', 'out_invoice')], required=True, string='Invoice')
    notification_user_id = fields.Many2one('res.users', string='Notify To',
                                           help='This user will be notify when Recurring Invoice is created')
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.user.company_id)
    interval_number = fields.Integer(string='Execute Every')
    interval_type = fields.Selection([('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months'),
                                      ('years', 'Years')], string='Interval Type', default='days', required=True)
    product_line_ids = fields.One2many('recurring.invoice.line', 'setting_invoice_id', string='Products')
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    stop_date = fields.Date(string='Stop Date', help='Onward this date recurring invoice will not be created', copy=False)
    next_execution_date = fields.Date(string='Next Execution Date', copy=False)
    recurred_invoice_ids = fields.Many2many('account.move', string='Orders', copy=False)
    recurred_invoices = fields.Integer(string='Recurred Invoices', compute='_get_recurred_invoices')


class RecurringInvoiceLine(models.Model):
    _name = 'recurring.invoice.line'
    _description = 'Products of recurring Invoice'

    setting_invoice_id = fields.Many2one('recurring.invoice.setting', string='Recurring Invoice Setting', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    account_id = fields.Many2one('account.account', string='Account')
    uom_id = fields.Many2one('uom.uom', string='UoM')
    description = fields.Char(string='Description')
    price = fields.Float(string='Unit Price')
    quantity = fields.Float(string='Quantity')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Line')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
