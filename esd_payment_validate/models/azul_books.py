# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AzulBooks(models.Model):

    _name = 'azul.books'

    mid = fields.Char(string='MID')
    subscription_id = fields.Char(string='SubscriptionId')
    group = fields.Char(string='Group')
    name = fields.Char(string='Name')
    ident_type = fields.Char(string='IdentType')
    ident_num = fields.Char(string='IdentNum')
    contract = fields.Char(string='Contract')
    card_number = fields.Char(string='CardNumber')
    currency = fields.Char(string='Currency')
    amount = fields.Float(string='Amount')
    tax = fields.Char(string='Tax')
    transaction_date = fields.Char(string='TransactionDate')
    transaction_type = fields.Char(string='TransactionType')
    approved = fields.Char(string='Approved')
    authorization_number = fields.Char(string='AuthorizationNumber')
    rrn = fields.Char(string='RRN')
    response_code = fields.Char(string='ResponseCode')
    response_message = fields.Char(string='ResponseMessage')