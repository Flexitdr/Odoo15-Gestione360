from odoo import models, fields, api, _
from datetime import datetime


class TxtPayrollWizard(models.TransientModel):
    _name = 'txt.payroll.wizard'
    _description = 'Generate TXT for Payroll'

    # def set_account_lines(self):
    #     selected_ids = self.env.context.get('active_ids', [])
    #     accounts = self.env['account.payment'].browse(selected_ids)
    #
    #     return accounts

    effective_date = fields.Date(string='Effective date', default=datetime.today())
    # account_payment_lines = fields.Many2many('account.payment', string='Payments providers', default=set_account_lines)

    def button_submit(self):
        selected_ids = self.env.context.get('active_ids', [])
        payslips = self.env['hr.payslip'].browse(selected_ids)
        return self.env['hr.payslip'].create_txt_payroll(payslips)



