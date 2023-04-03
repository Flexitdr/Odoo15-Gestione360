from odoo import models, fields, api


class InheritBankIds(models.Model):
    _inherit = 'res.partner.bank'

    code_bank_destination = fields.Selection([('10101070', 'BANCO POPULAR - 10101070'),
                                              ('10101010', 'BANCO DE RESERVAS - 10101010'),
                                              ('10101030', 'BANCO SCOTIABANK - 10101030'),
                                              ('10101060', 'CITIBANK - 10101060'),
                                              ('10101110', 'BANCO DEL PROGRESO - 10101110'),
                                              ('10101230', 'BANCO BHD LEON - 10101230'),
                                              ('10101300', 'BANCO DE DESARROLLO ADEMI - 10101300'),
                                              ('10101340', 'BANCO SANTA CRUZ - 10101340'),
                                              ('10101350', 'BANCO CARIBE - 10101350'),
                                              ('10101360', 'BANCO BDI - 10101360'),
                                              ('10101380', 'BANCO VIMENCA - 10101380'),
                                              ('10101390', 'BANCO LOPEZ DE ARO - 10101390'),
                                              ('10171228', 'BANCAMERICA - 10171228'),
                                              ('10172714', 'BANCO EMPIRE - 10172714'),
                                              ('10231034', 'ASOC. LA NACIONAL'),
                                              ('11101012', 'BANCO ATLANTICO - 11101012'),
                                              ('11102328', 'BANCO BANESCO - 11102328'),
                                              ('11121214', 'BANCO MULTIPLE LA FISE - 11121214'),
                                              ('11142133', 'BANCO BELLBANK - 11142133'),
                                              ('25311321', 'BANCO MULTIPLE ACTIVO - 25311321'),
                                              ('30232423', 'BANCO UNION - 30232423'),
                                              ('44405900', 'BANCO PROMERICA - 44405900'),
                                              ('47940900', 'ASOC. POPULAR DE AHORROS Y PRE. - 47940900'),
                                              ('48991200', 'ASOC. CIBAO DE A/P')], string='Rute bank')

    type_account = fields.Selection([('1', 'CUENTA CORRIENTE'), ('2', 'CUENTA DE AHORROS')], string='Type account')
    operation_code = fields.Selection([('22', 'CR. CUENTA CORRIENTE - 22'), ('32', 'CR. CUENTA DE AHORROS - 32')],
                                      string='Operation code')
    send_txt = fields.Boolean(string='Txt Bank Popular')


class InheritProvider(models.Model):
    _inherit = 'account.payment'

    state_pay_txt = fields.Selection([('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    description = fields.Text(required=True)
