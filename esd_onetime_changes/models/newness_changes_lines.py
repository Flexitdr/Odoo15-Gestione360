from odoo import models, fields, api
from datetime import date


class NewnessChangesLines(models.Model):
    _name = 'newness.changes.lines'

    name = fields.Many2one('newness.changes')
    employee_id = fields.Many2one('hr.employee')
    amount = fields.Float()
    start_date = fields.Date()
    end_date = fields.Date()
    pdo = fields.Selection(selection=[('1st', '1ra Quincena'), ('2nd', '2da Quincena')])
    state_newness = fields.Selection(selection=[('running', 'Running'), ('closed', 'Closed')],
                                     compute="_compute_state_newness")

    def _compute_state_newness(self):
        for rec in self:
            today = date.today()
            if rec.start_date <= today <= rec.end_date:
                rec.state_newness = 'running'
            else:
                rec.state_newness = 'closed'

