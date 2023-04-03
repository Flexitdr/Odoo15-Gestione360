from odoo import _, api, models, fields, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, Warning
import random
from datetime import datetime


class VisitSubscription(models.Model):
    _name = "visit.subscription"

    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    name = fields.Char(string='Name', default="New", compute='_compute_name', tore=True, required=True, readonly=True)
    equipment_id = fields.Many2one('esd.services.equipment', string='Equipment', readonly=True)
    reference_code = fields.Char(string='Reference', compute='_compute_reference_visit_subs', readonly=True)
    price = fields.Integer(string='Price', readonly=True)
    date = fields.Date(string='Fecha', readonly=True)
    state = fields.Selection([
        ('generated', 'Generated'),
        ('assigned', ' Assigned'),
        ('ready', 'Ready')], default='generated', readonly=True)
    sale_id = fields.Many2one(comodel_name='sale.order', string='Sale', required=False, readonly=True)
    last_maintenance = fields.Date(string='Last Maintenance', readonly=True)
    invoice_state = fields.Selection([
        ('not generated', 'Not Generated'),
        ('generated', ' Generated'),
        ('paid', 'Paid')], default='not generated', readonly=True)

    product_id = fields.Many2one('product.product', string='Product', readonly=True)

    def _compute_reference_visit_subs(self):

        fixed_digits = 8

        reference_code = random.randrange(11111111, 99999999, fixed_digits)

        for rec in self:

            if rec.reference_code:

                raise UserError(_('Sorry! This reference is already assigned, try again!'))

            rec.reference_code = 'vist - {}'.format(str(reference_code))

    @api.depends('reference_code')
    def _compute_name(self):
        """It displays record name as combination of short code, reference
        code and partner name """
        for rec in self:

            rec.name = 'VIST /' + rec.partner_id.name + ' - ' + rec.reference_code

    def button_create_invoice(self):

        partner_id = self.env['res.partner'].search([('id', '=', self.partner_id.id)])

        tax = self.env.company.account_sale_tax_id

        invoice_lines = []
        for rec in self:

            rec.invoice_state = 'generated'

            invoice_lines.append((0, 0, {
                'product_id': rec.product_id.id,
                'name': rec.name,
                'price_unit': rec.price,
                'tax_ids': tax
            }))

        self.env['account.move'].create(
            {
                'move_type': 'out_invoice',
                'date': fields.Date.today(),
                'invoice_date': fields.Date.today(),
                'partner_id': partner_id.id,
                'currency_id': partner_id.currency_id.id,
                'invoice_line_ids': invoice_lines,
                'journal_id': 1,
            })

        self.last_maintenance = datetime.today()
        self.equipment_id.create_next_maintenance()

