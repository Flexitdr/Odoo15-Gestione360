from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner'

    is_bank = fields.Boolean(
        string='Is Bank',
        required=False)