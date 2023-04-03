# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('validate', 'Validate')], string='Status', readonly=False)

    def button_validate_order(self):

        values = {
            'state': 'validate'
        }

        return self.write(values)

    def action_cancel(self):

        subs_cancel = super(SaleOrder, self)

        subs_client = self.env['subscription.package'].search([('sale_id', '=', self.id)])

        installation_client = self.env['esd.service.installation'].search([('sale_id', '=', self.id)])

        installation_client.cancel_request()

        subs_client.cancel_subs_stage()

        inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')

        inv.button_cancel()

        return self.write({'state': 'cancel', 'show_update_pricelist': False})