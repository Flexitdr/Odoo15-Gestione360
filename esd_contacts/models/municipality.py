from odoo import api, fields, models

class Municipality(models.Model):
    _name = 'esd.country.state.municipality'
    _description = 'Municipality'

    name = fields.Char(
        string='Name', 
        required=True)
    code = fields.Char(
        string='Code', 
        required=True)
    city_id = fields.Many2one(
        comodel_name='esd.country.city',
        string='City',
        required=False)
