# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TxtBanksPayroll(models.Model):
    _name = 'txt.bank.payroll'

    banks_id = fields.Many2one('res.bank', string='Bank')
    bank_digit_verify = fields.Char(string='Bank digit verification')


class TxtCompanyPayroll(models.Model):
    _name = 'txt.company.payroll'

    company_id = fields.Many2one('res.company', string='Company')
    company_id_number = fields.Char(string='Company ID number')
