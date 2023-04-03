from odoo import api, fields, models

class OfferSale(models.Model):
    _name = 'esd.offer.sale'
    _description = 'Offer Sale'

    name = fields.Char(
        string='Name',
        required=True)
    date_start = fields.Date(
        string='Date Start',
        required=True)
    date_end = fields.Date(
        string='Date End',
        required=True)
    payment_by_bank = fields.Boolean(
        string='Payment By Bank',
        required=False)
    bank_id = fields.Many2one(
        comodel_name='res.partner',
        string='Bank',
        required=False, domain="[('is_bank', '=', True)]")
    line_ids = fields.One2many(
        comodel_name='esd.offer.sale.line',
        inverse_name='offer_id',
        string='Line',
        required=False)
    is_financing_sale = fields.Boolean(
        string='Is Financing',
        required=False)

class OfferSaleLine(models.Model):
    _name = 'esd.offer.sale.line'
    _description = 'Offer Sale Line'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True)
    discount = fields.Float(
        string='Discount',
        required=True)
    offer_id = fields.Many2one(
        comodel_name='esd.offer.sale',
        string='Offer',
        required=False)