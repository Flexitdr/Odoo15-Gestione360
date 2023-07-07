
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError, Warning


class DgiiReportConfiguration(models.Model):
    _name = 'dgii.report.configuration'

    name = fields.Char(string='Name')
    tax_invoice_paid = fields.Boolean(string='Tax Invoice Paid', store=True)
    tax_invoice_generated = fields.Boolean(string='Tax Invoice Generated', store=True)

    @api.constrains('tax_invoice_paid', 'tax_invoice_generated')
    @api.onchange('tax_invoice_paid', 'tax_invoice_generated')
    def _check_unique(self):
        for record in self:
            if record.tax_invoice_paid and record.tax_invoice_generated:
                raise ValidationError('Only one tax type can be configured for the report')




