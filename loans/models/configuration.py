# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ConfigLoans(models.Model):
    _name = 'config.loans'
    _order = 'id desc'

    employee_id = fields.Many2one('hr.employee')
    amount_pre_approved = fields.Monetary(string='Total amount of credit approved')
    amount_taken = fields.Monetary(string='Total amount of loans taken')
    amount_available = fields.Monetary(string="Total amount of credit available")
    quota_limits = fields.Selection([('3', '3'), ('6', '6'), ('9', '9'), ('12', '12'), ('15', '15'), ('18', '18'),
                                     ('21', '21'), ('24', '24'), ('27', '27'), ('30', '30'), ('33', '33'), ('36', '36'),
                                     ('39', '39'), ('42', '42'), ('45', '45'), ('48', '48')], string='Quota limit')
    current_interest_rate = fields.Char(string='Current interest rate')

    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    @api.onchange('amount_taken')
    def set_amount_available(self):
        total = self.amount_pre_approved - self.amount_taken
        self.amount_available = total
