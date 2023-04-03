from odoo import api, fields, models

class TypeDocument(models.Model):
    _name = 'esd.type.document'
    _description = 'Type Document'

    name = fields.Char(
        string='Name',
        required=True)
    is_individual = fields.Boolean(
        string='Is individual',
        required=False)
    is_company = fields.Boolean(
        string='Is company',
        required=False)

class SaleDocumentLine(models.Model):
    _name = 'esd.sale.document'
    _description = 'Sale Document Line'

    name = fields.Many2one(
        comodel_name='esd.type.document',
        string='Name',
        required=False)
    filename = fields.Char(
        string='Filename',
        required=False)
    file_document = fields.Binary(string="File", )
    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale',
        required=False)




