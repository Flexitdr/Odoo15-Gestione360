from odoo import models, fields, api


class RequestsNewnessLines(models.Model):
    _name = 'requests.newness.lines'

    newness = fields.Many2one('newness.changes', required=True)
    amount = fields.Float(required=True)
    requests_id = fields.Many2one('requests.newness')
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
