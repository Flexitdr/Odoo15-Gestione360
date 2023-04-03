# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class CommissionLine(models.Model):

    _inherit = 'commission.line'


    @api.model
    def get_commisions(self, user, date_from, date_to):

        commissions = self.env['commission.line'].search([('user_id', '=', user.id),
                                                          ('date', '>=', date_from),
                                                          ('date', '<=', date_to)])

        total = 0.0

        for commission in commissions:

            total += commission.commission_amount

        return total

