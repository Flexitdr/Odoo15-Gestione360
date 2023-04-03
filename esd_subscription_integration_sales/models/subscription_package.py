# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError
import json
import logging
from datetime import timedelta
from collections import defaultdict
from datetime import datetime


class SubscriptionPackage(models.Model):
    _inherit = 'subscription.package'

    equipment_id = fields.Many2one('esd.services.equipment', string='Equipment')

    # @api.onchange('equipment_id')
    # def verify_equipment_serial(self):
    #
    #     for rec in self:
    #
    #         if rec.equipment_id:
    #
    #             raise UserError(_('Sorry! This serial is already assigned, try again!'))




