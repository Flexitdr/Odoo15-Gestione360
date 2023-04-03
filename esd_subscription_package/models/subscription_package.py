from odoo import _, api, models, fields, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import random
import asyncio


class SubscriptionPackage(models.Model):
    _inherit = 'subscription.package'

    recurring_invoices = fields.Many2many('account.move', string='invoice',
                                          domain="[('partner_id', '=', partner_id)]",
                                          compute='_compute_recurring_invoices')

    subscription_duration = fields.Datetime(string='Duration')

    total_recurring_price = fields.Float()

    stage_id = fields.Many2one('subscription.package.stage', string='Stage',
                               default=lambda self: self._default_stage_id(),
                               index=True,
                               group_expand='_read_group_stage_ids', store=True,
                               compute="_compute_expiration_alert")

    company_id = fields.Many2one('res.company', string='Company', store=True)

    product_line_ids = fields.One2many('subscription.package.product.line',
                                       'subscription_id', ondelete='restrict',
                                       string='Products Line')
    invoice_count = fields.Char(string='Invoices', compute='_compute_invoice_count')

    invoice_recurrence_count = fields.Char(string='Invoices', compute='_compute_invoice_recurrence_count')

    next_invoice_date = fields.Date(string='Next Invoice Date', readonly=False,
                                    store=True,
                                    compute="_compute_next_invoice_date")

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')
    tag_ids = fields.Many2many('account.analytic.tag', string='Tags')

    payment_format = fields.Selection([
        ('1', '1 Month'),
        ('3', '3 Month'),
        ('6', '6 Month'),
        ('12', '1 Year')], default='1')

    responsible_collect = fields.Many2one('res.users', string='Responsible for Collect',
                                          domain=lambda self: [('groups_id', 'in', self.env.ref(
                                              'esd_subscription_package.subscription_user').id)])

    sale_id = fields.Many2one(comodel_name='sale.order', string='Sale', required=False)

    edit_price = fields.Float(string='Edit Price')

    @api.depends('payment_format')
    def _compute_next_invoice_date(self):

        pending_subscriptions = self.env['subscription.package'].search(
            [('stage_category', '=', 'progress')])
        for sub in pending_subscriptions:
            if sub.start_date:
                sub.next_invoice_date = sub.start_date + relativedelta(months=1 * int(sub.payment_format))

    @api.depends('invoice_count')
    def _compute_invoice_recurrence_count(self):

        for rec in self:

            invoice_recurrence_count = self.env['subscription.payment.line'].search(
                [('reference_code', '=', rec.reference_code)])
            if len(invoice_recurrence_count) > 0:

                count = rec.env['subscription.package.plan'].search([('id', '=', rec.plan_id.id)])

                payment_qty = count.limit_count / int(rec.payment_format)

                rec.invoice_recurrence_count = "{}/{}".format(len(invoice_recurrence_count), round(payment_qty))
            else:
                rec.invoice_recurrence_count = 0

    @api.depends('invoice_count')
    def _compute_invoice_count(self):
        """ Calculate Invoice count based on subscription package """
        invoice_count = self.env['account.move'].search_count(
            [('subscription_id', '=', self.id)])
        if invoice_count > 0:

            count = self.env['subscription.package.plan'].search([('id', '=', self.plan_id.id)])

            self.invoice_count = "{} / {}".format(invoice_count, count.limit_count)
        else:
            self.invoice_count = 0

    @api.depends('reference_code')
    def _compute_name(self):
        """It displays record name as combination of short code, reference
        code and partner name """
        for rec in self:
            if rec.current_stage == 'draft':
                rec.name = 'SUBS /' + rec.partner_id.name

    def _compute_recurring_invoices(self):
        for rec in self:
            res = []
            recurring = self.env['account.move'].search([('partner_id', '=', self.partner_id.id),
                                                         ('is_recurrence', '=', True)])

            for row in recurring:
                res.append(row.id)

            rec.recurring_invoices = [(6, 0, res)]

    # @api.depends('product_line_ids.total_amount', 'next_invoice_date')
    # def _compute_total_recurring_price(self):
    #     stage = self.env['subscription.package.stage'].search(
    #         [('category', '=', 'progress')], limit=1).id
    #
    #     for rec in self:
    #         if not rec.stage_id.id == stage:
    #             total_recurring = 0
    #             for line in rec.product_line_ids:
    #                 total_recurring += line.total_amount
    #             rec['total_recurring_price'] = total_recurring

    @api.depends('next_invoice_date', 'subscription_duration', 'stage_id')
    async def _compute_expiration_alert(self):

        stage = self.env['subscription.package.stage'].search(
            [('category', '=', 'progress')], limit=1).id

        for rec in self:
            if rec.stage_id.id == stage:
                duration = datetime.strptime(str(rec.subscription_duration), '%Y-%m-%d %H:%M:%S')
                next_invoice = datetime.strptime(str(rec.next_invoice_date), '%Y-%m-%d')

                if next_invoice + relativedelta(months=2) > duration and rec.payment_format != '12':
                    stage = self.env['subscription.package.stage'].search(
                        [('category', '=', 'expiration')], limit=1).id
                    for sub in self:
                        values = {'stage_id': stage}
                        await sub.send_expiration_mail()
                        sub.write(values)

    @api.onchange('edit_price')
    def onchange_total_recurring_price(self):

        self.total_recurring_price = self.edit_price

    def unlink(self):
        for rec in self:
            if rec.current_stage == 'progress':
                raise UserError(_('Sorry! You can not delete a '
                                  'subscription in process first cancel it!'))

        return super().unlink()

    def button_start_date(self):
        start = date.today()

        for rec in self:

            duration = rec.env['subscription.package.plan'].search([('id', '=', rec.plan_id.id)])
            exact_duration = start + relativedelta(months=duration.limit_count)
            rec.subscription_duration = datetime.strftime(exact_duration, '%Y-%m-%d')

            rec.subscription_payment_line()

        return super(SubscriptionPackage, self).button_start_date()

    def subscription_payment_line(self):

        for line in self:

            fixed_digits = 8

            count = line.env['subscription.package.plan'].search([('id', '=', line.plan_id.id)])

            payment_qty = count.limit_count / int(line.payment_format)

            qty_fee_calculation = "{}/{}".format(1, round(payment_qty))

            subs_client = line.env['subscription.payment.line'].search([('reference_code', '=', line.reference_code)])

            if not subs_client:

                self.env['subscription.payment.line'].create({
                    'currency_id': line.currency_id.id,
                    'partner_id': line.partner_id.id,
                    'reference_code': line.reference_code,
                    'company_id': line.company_id.id,
                    'recurring_price': float(line.total_recurring_price),
                    'plan_id': line.plan_id.id,
                    'equipment': line.equipment_id.id,
                    'plan_duration': line.subscription_duration,
                    'payment_format': line.payment_format,
                    'product_qty': line.product_line_ids.product_qty,
                    'qty_fee': qty_fee_calculation,
                    'invoice_code': random.randrange(11111111, 99999999, fixed_digits)

                })

            if subs_client:

                for a in subs_client[-1]:
                    count_position = int(a.qty_fee[0]) + 1

                    payment_qty = count.limit_count / int(line.payment_format)

                    qty_fee_calculation_existing = "{}/{}".format(count_position, round(payment_qty))

                    self.env['subscription.payment.line'].create({
                        'currency_id': line.currency_id.id,
                        'partner_id': line.partner_id.id,
                        'reference_code': line.reference_code,
                        'company_id': line.company_id.id,
                        'recurring_price': float(line.total_recurring_price),
                        'plan_id': line.plan_id.id,
                        'equipment': line.equipment_id.id,
                        'plan_duration': line.subscription_duration,
                        'payment_format': line.payment_format,
                        'product_qty': line.product_line_ids.product_qty,
                        'qty_fee': qty_fee_calculation_existing,
                        'invoice_code': random.randrange(111111, 999999, fixed_digits)

                    })

    def close_subscription(self):
        for rec in self:
            if rec.subscription_duration < rec.next_invoice_date:
                return rec.button_close()

    def button_subscription_information(self):
        res = []

        subscription = self.env['subscription.package'].search([('partner_id', '=', self.partner_id.id)])

        for row in subscription:
            res.append(row.id)

        renew_active = self.env['renew.subscription'].search([('partner', '=', self.partner_id.id)])

        if renew_active.subscription_state == 'in process':
            raise UserError(_('Sorry! this partner has payment process, '
                              'go to renew information to see!'))

        else:

            return {
                'name': 'Subscription Information',
                'view_type': 'form',
                'res_model': 'renew.subscription',
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
                'context': {
                    "create": True,
                    'default_partner': self.partner_id.id,
                    'default_subscriptions': [(6, 0, res)]
                }
            }

    def send_expiration_mail(self):

        mail_template = self.env.ref('esd_subscription_package.mail_template_esd_subscription_renew_auto')
        mail_template.send_mail(self.ids[0], force_send=True)

    def change_subscription_stage(self):

        stage = self.env['subscription.package.stage'].search(
            [('category', '=', 'approved')], limit=1).id

        values = {
            'stage_id': stage
        }

        return self.write(values)

    def cancel_subs_stage(self):
        stage = self.env['subscription.package.stage'].search(
            [('category', '=', 'cancel')], limit=1).id

        values = {
            'stage_id': stage,
        }

        return self.write(values)

    def button_close(self):
        for rec in self:
            rec.equipment_id.stop_maintenance()

        return super().button_close()

    def button_invoice_recurrence_count(self):
        """ It displays invoice based on subscription package """
        return {
            'name': 'Recurrence',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'view_type': 'form',
            'res_model': 'subscription.payment.line',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                "create": False
            }
        }

    @api.depends('next_invoice_date')
    def calculate_old_date(self):
        today = date.today()

        subs = self.env['subscription.package'].search(
            [('current_stage', 'in', ('progress', 'expiration', 'approved'))])

        a = 0

        for partner in subs.partner_id:

            subs_ids = subs.filtered(lambda r: r.partner_id.id == partner.id)

            if datetime.strftime(today, '%Y-%m-%d') > datetime.strftime(subs_ids[0].next_invoice_date, '%Y-%m-%d'):

                for sub in subs_ids:

                    sub.subscription_payment_line()
                    sub.next_invoice_date = sub.next_invoice_date + relativedelta(months=1 * int(sub.payment_format))
                    print('es hoy')

            else:
                print('No es hoy {}'.format(a))
                a += 1
                continue

    @api.depends('next_invoice_date')
    def calculate_next_invoice_subs(self):
        today = date.today()

        subs = self.env['subscription.package'].search(
            [('current_stage', 'in', ('progress', 'expiration', 'approved'))])

        a = 0

        for partner in subs.partner_id:

            subs_ids = subs.filtered(lambda r: r.partner_id.id == partner.id)

            if datetime.strftime(today, '%Y-%m-%d') == datetime.strftime(subs_ids[0].next_invoice_date, '%Y-%m-%d'):

                for sub in subs_ids:

                    sub.subscription_payment_line()
                    sub.next_invoice_date = today + relativedelta(months=1 * int(sub.payment_format))
                    print('es hoy')

            else:
                print('No es hoy {}'.format(a))
                a += 1
                continue

    @api.onchange('subscription_duration')
    def active_subscription_plan_by_payment(self):
        today = date.today()

        subs = self.env['subscription.package'].search(
            [('current_stage', 'in', ('expiration', 'approved'))])

        for rec in subs:

            stage = self.env['subscription.package.stage'].search(
                [('category', '=', 'progress')], limit=1).id

            if datetime.strftime(today, '%Y-%m-%d') == datetime.strftime(rec.subscription_duration,
                                                                         '%Y-%m-%d') and rec.to_renew:

                next_invoice = today + relativedelta(months=1 * int(rec.payment_format))

                values = {
                    'stage_id': stage,
                    'start_date': today,
                    'next_invoice_date': next_invoice,
                    'subscription_duration': today + relativedelta(years=1),
                    'to_renew': False,
                    'reference_code': self.env['ir.sequence'].next_by_code('sequence.reference.code') or 'New'

                }

                rec.write(values)

    @api.onchange('stage_id')
    def renew_subscription_plan(self):

        today = date.today()

        for rec in self:

            invoice_recurrence_count = self.env['subscription.payment.line'].search(
                [('reference_code', '=', rec.reference_code)])

            payment_qty = rec.plan_id.limit_count / int(rec.payment_format)

            if len(invoice_recurrence_count) >= round(payment_qty) and rec.current_stage == 'closed':

                stage = self.env['subscription.package.stage'].search(
                    [('category', '=', 'progress')], limit=1).id

                next_invoice = today + relativedelta(months=1 * int(rec.payment_format))

                values = {
                    'stage_id': stage,
                    'start_date': today,
                    'next_invoice_date': next_invoice,
                    'subscription_duration': today + relativedelta(years=1),
                    'to_renew': False,
                    'reference_code': self.env['ir.sequence'].next_by_code('sequence.reference.code') or 'New'
                }

                rec.write(values)
