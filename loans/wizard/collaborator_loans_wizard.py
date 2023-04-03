from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CollaboratorLoansWizard(models.TransientModel):
    _name = 'collaborator.loans.wizard'
    _description = 'Collaborator Loans Wizard'

    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    amount_request = fields.Monetary(string='Amount to request')
    interest_rate = fields.Char(string='Interest Rate')
    quota_quantity = fields.Selection([('3', '3'), ('6', '6'), ('9', '9'), ('12', '12'), ('15', '15'), ('18', '18'),
                                     ('21', '21'), ('24', '24'), ('27', '27'), ('30', '30'), ('33', '33'), ('36', '36'),
                                     ('39', '39'), ('42', '42'), ('45', '45'), ('48', '48')], string='Quantity quotas',
                                      default='3')
    quota_amount = fields.Monetary(string='Amount of quotas')
    terms_and_conditions = fields.Boolean(string='Terms and Conditions')
    signature = fields.Text(required=True, string='Signature here')

    def button_submit(self):
        self.ensure_one()
        this_req_id = self.env.context.get('active_id')
        req = self.env['collaborator.loans'].search([('id', '=', this_req_id)])
        if not self.terms_and_conditions:
            raise UserError(_('You must agree to the terms and conditions.'))
        req.state = 'in_validation'
        req.loan_status = req.state

    # @api.onchange('quota_quantity')
    # def set_interest_rate(self):
    #     data = self.env['interest.rate'].search([('start_quota', '=', self.quota_quantity)])
    #     if int(data.start_quota) < int(data.end_quota):
    #         self.interest_rate = data.interest_rate
