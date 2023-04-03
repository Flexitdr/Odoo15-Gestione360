# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit   = fields.Boolean('Permitir Sobre Crédito?')
    overdue_bills = fields.Boolean('Facturar con Facturas Vencidas?')
    allow_days    = fields.Integer('Días de Gracias')
    block_credit  = fields.Boolean('Bloquear Crédito?',default=False)