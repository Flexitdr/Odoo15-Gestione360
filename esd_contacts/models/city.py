from odoo import api, fields, models 


class City(models.Model):
    _name = 'esd.country.city'
    _description = 'City'

    name = fields.Char(
        string='Name',
        required=True)
    code = fields.Char(
        string='Code',
        required=True)
    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='State',
        required=True)
    
