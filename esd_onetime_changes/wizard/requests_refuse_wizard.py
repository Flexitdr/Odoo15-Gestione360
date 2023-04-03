from odoo import models, fields, api


class RequestsRefuseWizard(models.TransientModel):
    _name = 'requests.refuse.wizard'
    _description = 'Requests Refuse Wizard'

    refuse_reason = fields.Text(required=True, string='Close Reason')
    closed_by = fields.Many2one('hr.employee', readonly=True,
                                default=lambda self: self.env.user.employee_id and self.env.user.employee_id.id or False)
    close_date = fields.Date(string='Closed On', default=lambda self: fields.Date.today())

    def button_submit(self):
        self.ensure_one()
        this_req_id = self.env.context.get('active_id')
        req = self.env['requests.newness'].search([('id', '=', this_req_id)])
        req.is_closed = True
        req.refuse_reason = self.refuse_reason
        req.closed_by = self.closed_by
        req.close_date = self.close_date
        req.state = 'refuse'
