# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TxtBanksProviders(models.Model):
    _name = 'txt.banks.config'

    banks_id = fields.Many2one('res.bank', string='Bank')
    bank_digit_verify = fields.Char(string='Bank digit verification')


class TxtCompany(models.Model):
    _name = 'txt.company.config'

    company_id = fields.Many2one('res.company', string='Company')
    company_id_number = fields.Char(string='Company ID number')
