from odoo import models, fields, api, _
from datetime import datetime


class TxtProvidersWizard(models.TransientModel):
    _name = 'txt.providers.wizard'
    _description = 'Collaborator Loans Wizard'

    def set_account_lines(self):
        selected_ids = self.env.context.get('active_ids', [])
        accounts = self.env['account.payment'].browse(selected_ids)

        return accounts

    effective_date = fields.Date(string='Effective date', default=datetime.today())
    account_payment_lines = fields.Many2many('account.payment', string='Payments providers', default=set_account_lines)

    def button_submit(self):
        selected_ids = self.env.context.get('active_ids', [])
        accounts = self.env['account.payment'].browse(selected_ids)
        return self.env['account.payment'].create_txt_provider(accounts)



