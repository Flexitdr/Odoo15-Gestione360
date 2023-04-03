from odoo import api, fields, models


class AccountResCont(models.Model):
    _inherit = 'account.move'

    responsible_collect = fields.Many2one('hr.employee')

    @api.onchange('partner_id')
    def get_responsible_collect(self):
        partner = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
        self.responsible_collect = partner.assigned_collector.id

    payment_filename = fields.Char(
        string='Payment Filename',
        required=False)
    payment_file = fields.Binary(string="Payment Document", )
    purchase_filename = fields.Char(
        string='Purchase Filename',
        required=False)
    purchase_file = fields.Binary(string="Purchase Order", )
