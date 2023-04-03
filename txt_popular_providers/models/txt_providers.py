# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from datetime import datetime


class TxtProviders(models.Model):
    _inherit = 'account.payment'

    txt_providers = fields.Binary()

    def button_txt_providers_wizard(self):
        return {
            'name': "Txt payment providers",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'txt.providers.wizard',
            'target': 'new',
        }

    @api.model
    def create_txt_provider(self, values):
        # Create the Header
        company = self.env.company
        sequence = self.env['ir.sequence'].next_by_code('header.sequence') or 'New'
        type_service = "02"
        effective_date = datetime.strptime(self._context['effective_date'], '%Y-%m-%d').strftime('%Y%m%d')
        debit_quantity = '00000000000'
        debit_total_amount = '0000000000000'
        credit_quantity = f'{len(values):011}'
        sum_credit = 0.00

        for value in values:
            sum_credit += value.amount

        credit_total_amount = '{:.2f}'.format(sum_credit).replace('.', '').rjust(13, '0')
        mid_affiliation = '000000000000000'
        date_send = datetime.today().strftime('%Y%m%d')
        send_time = datetime.now().strftime('%H%M')
        employee_email = self.env['hr.employee'].search([
            ('id', '=', self.env.user.employee_id and self.env.user.employee_id.id or False)]).work_email

        header = 'H{}{}{}{}{}{}{}{}{}{}{}{}{}'.format(company.vat.ljust(15), company.name.ljust(35), sequence,
                                                      type_service, effective_date, debit_quantity, debit_total_amount,
                                                      credit_quantity, credit_total_amount, mid_affiliation,
                                                      date_send, send_time, employee_email.ljust(40))
        # Create the Body
        with open('tmp/data.txt', 'w') as f:
            f.write('{}\n'.format(header))
            reference_number = self.env['ir.sequence'].next_by_code('reference.number.sequence') or 'New'
            count = 0
            for value in values:
                value.state_pay_txt = 'paid'
                bank = value.partner_id.bank_ids.filtered(lambda x: x.send_txt is True)
                name = '%.35s' % value.invoice_partner_display_name.ljust(35)  # limit to 35 characters
                count += 1
                transaction_sequence = f'{count:07}'

                account_destination = '{}'.format(bank.acc_number).ljust(20)
                type_account = bank.type_account

                if value.currency_id.display_name == 'DOP':
                    currency_destination = '214'
                if value.currency_id.display_name == 'USD':
                    currency_destination = '840'
                if value.currency_id.display_name == 'EUR':
                    currency_destination = '978'

                bank_code = bank.code_bank_destination
                verification_code_bank = \
                    self.env['txt.banks.config'].search([('banks_id', '=', bank.bank_id.id)]).bank_digit_verify
                operation_code = bank.operation_code
                transaction_amount = '{:.2f}'.format(value.amount).replace('.', '').rjust(13, '0')

                if not str.isdigit(value.partner_id.vat):
                    type_identification = 'PS'
                if len(value.partner_id.vat) < 11:
                    type_identification = 'RN'
                if len(value.partner_id.vat) >= 11:
                    type_identification = 'CE'

                identification_number = value.partner_id.vat.ljust(15)
                description = '%.40s' % value.description.ljust(40)
                due_date = ''.ljust(4)
                contact_form = '1'
                fax_telephone = ''.ljust(12)
                paid_process = '00'

                f.write('N{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}\n'.format(company.vat.ljust(15), sequence, transaction_sequence,
                                                            account_destination, type_account, currency_destination,
                                                            bank_code, verification_code_bank, operation_code,
                                                            transaction_amount, type_identification, identification_number,
                                                            name, reference_number.ljust(12), description, due_date, contact_form,
                                                            employee_email.ljust(40), fax_telephone, paid_process))

            f.close()

        x = open('tmp/data.txt', 'r')
        body_to_show = x.read()

        file_data = base64.b64encode(body_to_show.encode())

        company_code = \
            self.env['txt.company.config'].search([('company_id', '=', self.env.company.id)]).company_id_number

        day_month = datetime.today().strftime('%m%d')
        header_sequence_file = self.env['ir.sequence'].next_by_code('field.name.sequence') or 'New'

        name_file = "PE{}{}{}{}E.txt".format(company_code, type_service, day_month, header_sequence_file)

        values = {
            'name': name_file,
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': file_data,
        }

        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': str(base_url) + str(download_url)
        }

