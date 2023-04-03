# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api, _


class CreditCards(models.Model):
    _name = 'credit.cards'
    _order = 'id desc'

    type_of_document = fields.Selection(selection=[('rnc', 'RNC'), ('cedula', 'Cedula'),
                                                   ('passport', 'Passport')])
    document = fields.Char(string='Number of document')
    titular = fields.Char(string='name of titular')
    type_of_card = fields.Selection(selection=[('mastercard', 'Mastercard'), ('visa', 'Visa'),
                                               ('american express', 'American Express'), ('other', 'Other')])
    number_card = fields.Char(string="Number of card")
    expiration_date = fields.Char(string="Expiration date MM/AA")
    terms_and_conditions = fields.Boolean(string="Terms and Conditions")
    storage_card = fields.Char(string="Storage Card")
    order_number = fields.Char(string="Order Number")
    is_visible = fields.Boolean(string="Is Visible")
