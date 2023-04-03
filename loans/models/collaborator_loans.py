# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class CollaboratorLoans(models.Model):
    _name = 'collaborator.loans'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('draft', 'Draft'), ('in_validation', 'In Validation'), ('in_action', 'In Action'),
                              ('finalized', 'Finalized'), ('legal', 'Legal'), ('refused', 'Refused')],
                             default='draft', string='Status')
    collaborator_name = fields.Many2one(
        'hr.employee', default=lambda self: self.env.user.employee_id and self.env.user.employee_id.id or False)
    collaborator_number = fields.Char(string='Collaborator Number', compute='_compute_fill_collaborator')
    actual_position = fields.Char(string='Current Position', readonly=True)
    sex = fields.Char(string='Sex', readonly=True)
    telephone = fields.Char(string='Telephone', readonly=True)
    mobile = fields.Char(string='Mobile', readonly=True)
    email = fields.Char(string='Email', readonly=True)
    address = fields.Char(string='Address', readonly=True)

    loan_date = fields.Date(string='Loan date', default=datetime.today())
    loan_number = fields.Char(string='Loan number')
    loan_type = fields.Selection([('vehicle', 'Vehicle'), ('personal', 'Personal')], string='Loan Type')
    loan_status = fields.Char(string='Loan status')
    loan_amount = fields.Char(string='Loan amount')
    interest_rate = fields.Char(string='Interest rate')
    quota_status = fields.Char(string='Quota status')
    next_payment_date = fields.Char(string='Next payment day')
    quota_amount = fields.Char(string='Quota amount')
    delay_amount = fields.Char(string='Delay amount')
    other_charges = fields.Char(string='Other charges')
    loan_balance = fields.Char(string='Loan balance')

    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    amount_pre_approved = fields.Monetary(string='Total amount of credit approved', readonly=True)
    amount_loans_taken = fields.Monetary(string='Total amount of loans taken', readonly=True)
    amount_available = fields.Monetary(string="Total amount of credit available", readonly=True)
    quota_limits = fields.Char(string='Quota limit', readonly=True)
    current_interest_rate = fields.Char(string='Current interest rate', readonly=True)
    is_visible = fields.Boolean()

    def button_wizard(self):
        return {
            'name': "Collaborator Loans Wizard",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'collaborator.loans.wizard',
            'target': 'new'
        }

    def action_refuse(self):
        self.state = 'refused'

    @api.onchange('collaborator_name')
    def _compute_fill_collaborator(self):
        emp = self.collaborator_name
        config = self.env['config.loans'].search([('employee_id', '=', emp.id)])
        self.collaborator_number = emp.code
        self.actual_position = emp.department_id.name
        self.sex = emp.gender
        self.telephone = emp.work_phone
        self.mobile = emp.mobile_phone
        self.email = emp.work_email
        self.address = emp.address_home_id.contact_address

        self.amount_pre_approved = config.amount_pre_approved
        self.amount_loans_taken = config.amount_taken
        self.amount_available = config.amount_available
        self.quota_limits = config.quota_limits
        self.current_interest_rate = config.current_interest_rate

    @api.onchange('state')
    def set_loan_status(self):
        self.loan_status = self.state
