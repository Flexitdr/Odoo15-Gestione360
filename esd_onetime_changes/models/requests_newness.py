from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class RequestsNewness(models.Model):
    _name = 'requests.newness'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string='Application date', required=True, default=datetime.today())
    newness_id = fields.One2many('requests.newness.lines', 'requests_id')
    employee = fields.Many2one('hr.employee', required=True)
    requester = fields.Many2one('hr.employee', readonly=True,
                                default=lambda self: self.env.user.employee_id and self.env.user.employee_id.id or False)
    state = fields.Selection([('created', 'Created'), ('confirmed', 'Confirmed'), ('validated', 'Validated'),
                              ('refuse', 'Refused')], default='created', string='Status')
    pdo = fields.Selection(selection=[('1st', '1ra Quincena'), ('2nd', '2da Quincena')], required=True)

    is_closed = fields.Boolean(string="Closed", default=False)
    closed_by = fields.Many2one('hr.employee', string='Closed By', readonly=True)
    close_date = fields.Date(string='Closed on', readonly=True)
    refuse_reason = fields.Text(string='Close Reason', readonly=True)

    def action_confirm(self):
        self.state = 'confirmed'

    def action_validate(self):
        if self.state == 'created':
            raise UserError("You cannot validate the request without having previously confirmed it.")
        else:
            self.ensure_one()
            hr = self.env['hr.employee'].search([('id', '=', self.employee.id)])
            req = self.env['requests.newness'].search([('id', '=', self.id)])
            newness_lines = []
            for new_line in req.newness_id:
                newness_lines.append((0, 0, {
                    'name': new_line.newness.id,
                    'amount': new_line.amount,
                    'start_date': new_line.start_date,
                    'end_date': new_line.end_date,
                    'pdo': req.pdo
                }))
            hr.hr_newsness = newness_lines
            self.state = 'validated'

    def action_refuse(self):
        return {
            'name': "Requests Refuse Reason",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'requests.refuse.wizard',
            'target': 'new'
        }

    @api.model
    def create(self, vals):
        if not vals.get('newness_id'):
            raise ValidationError(_("You must provide a newness"))
        res = super(RequestsNewness, self).create(vals)
        return res
