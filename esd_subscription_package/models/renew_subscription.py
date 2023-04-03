from odoo import _, api, models, fields, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, Warning
# from ..controllers.esd_azul_request import open_azul_form


class RenewSubscription(models.Model):
    _name = 'renew.subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', default="New", compute='_compute_name',
                       store=True, required=True)
    partner = fields.Many2one('res.partner', string='Client')
    subscriptions = fields.Many2many('subscription.package', string='Subscriptions',
                                     domain="[('partner_id', '=', partner)]")
    seller = fields.Many2one('hr.employee', readonly=True,
                             default=lambda self: self.env.user.employee_id and self.env.user.employee_id.id or False)
    subscription_information = fields.Binary(string='Upload Conversation')
    subscription_state = fields.Selection([('in process', 'In Process'), ('confirmed', 'Confirmed')],
                                          defauld='in process')
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', store=True)

    @api.depends('partner')
    def _compute_name(self):

        for rec in self:
            if rec.partner and rec.subscriptions.reference_code:
                rec.name = rec.partner.name + '/' + rec.subscriptions.reference_code

    @api.model
    def create(self, values):

        if values.get('subscription_state'):
            raise UserError(_('Sorry! You can add two renew request of same client in process!'))

        return super().create(values)

    def action_in_process(self):
        values = {
            'subscription_state': 'in process',
        }
        return self.write(values)

    def payment_made(self):
        #TODO: payment confirmation code here

        values = {
            'subscription_state': 'confirmed',
        }
        return self.write(values)

    def action_send_email(self):
        mail_template = self.env.ref('esd_subscription_package.mail_template_esd_subscription_renew')
        for rec in self:
            mail_template.send_mail(rec.id, force_send=True)

            values = {
                'subscription_state': 'in process',
            }

            rec.env['subscription.package'].search([('partner_id', '=', self.partner.id),
                                                    ('reference_code', '=',
                                                     self.subscriptions.reference_code, )]).change_subscription_stage()

            return self.write(values)

    # def open_azul_form(self, res):
    #
    #     return open_azul_form(res)








