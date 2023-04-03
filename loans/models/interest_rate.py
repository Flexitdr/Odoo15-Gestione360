# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InterestRateLoans(models.Model):
    _name = 'interest.rate'

    start_quota = fields.Selection([('3', '3'), ('6', '6'), ('9', '9'), ('12', '12'), ('15', '15'), ('18', '18'),
                                     ('21', '21'), ('24', '24'), ('27', '27'), ('30', '30'), ('33', '33'), ('36', '36'),
                                     ('39', '39'), ('42', '42'), ('45', '45'), ('48', '48')], string='Start Quota')

    end_quota = fields.Selection([('3', '3'), ('6', '6'), ('9', '9'), ('12', '12'), ('15', '15'), ('18', '18'),
                                    ('21', '21'), ('24', '24'), ('27', '27'), ('30', '30'), ('33', '33'), ('36', '36'),
                                    ('39', '39'), ('42', '42'), ('45', '45'), ('48', '48')], string='Start Quota')

    interest_rate = fields.Char(string='Interest Rate')
