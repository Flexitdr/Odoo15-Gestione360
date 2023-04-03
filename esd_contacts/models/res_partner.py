from odoo import api, fields, models, _
from odoo import exceptions
from odoo.exceptions import UserError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one(
        comodel_name='esd.country.city',
        string='City',
        required=False, domain="[('state_id', '=', state_id)]")
    municipality_id = fields.Many2one(
        comodel_name='esd.country.state.municipality',
        string='Municipality',
        required=False, domain="[('city_id', '=', city_id)]")
    zone_id = fields.Many2one(
        comodel_name='esd.country.state.municipality.zone',
        string='Zone',
        required=False, domain="[('municipality_id', '=', municipality_id)]")
    relationship = fields.Selection(
        string='Relationship',
        selection=[('parent', 'Parent'),
                   ('child', 'Child'),
                   ('couple', 'Couple'),
                   ('friend', 'Friend'),
                   ('employee', 'Employee'),
                   ('other', 'Other'),
                   ],
        required=False, )
    assigned_collector = fields.Many2one(
        comodel_name='hr.employee',
        string='Assigned Collector',
        required=False)

    phone = fields.Char(size=10)
    mobile = fields.Char(size=10)
        

    @api.onchange('phone')
    def _onchange_validate_phone(self):

        if self.phone:
            regex = "^(\(?[\d]{1,3}\)?)\s?([\d]{1,5})\s?([\d][\s\.-|.]?){6,7}$"
            result = re.match(regex, self.phone)

            if result is None:
                raise exceptions.ValidationError(_("Invalid phone number."))

    @api.onchange('mobile')
    def _onchange_validate_mobile(self):
        if self.mobile:
            regex = "^(\(?[\d]{1,3}\)?)\s?([\d]{1,5})\s?([\d][\s\.-|.]?){6,7}$"
            result = re.match(regex, self.mobile)

            if result is None:
                raise exceptions.ValidationError(_("Invalid mobile number."))

    @api.onchange('email')
    def _onchange_validate_email(self):
        if self.email:
            regex = "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+[.com.do]$"
            result = re.match(regex, self.email)

            if result is None:
                raise exceptions.ValidationError(_("Invalid email address."))

    @api.model
    def create(self, vals):
        contacts = self.env['res.partner'].search([])
        for contact in contacts:
            if vals.get('vat') == contact.vat:
                raise UserError("This contact has already been created")
        if vals['name']:
            vals['name'] = vals['name'].upper()

        res = super(ResPartner, self).create(vals)

        return res
