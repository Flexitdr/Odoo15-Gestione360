from odoo import api, fields, models 

class Zone(models.Model):
    _name = 'esd.country.state.municipality.zone'
    _description = 'Zone'

    name = fields.Char(
        string='Name',
        required=True)
    code = fields.Char(
        string='Code',
        required=True)
    municipality_id = fields.Many2one(
        comodel_name='esd.country.state.municipality',
        string='Municipality',
        required=True)
    
