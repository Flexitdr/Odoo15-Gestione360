from odoo import models, fields, api


class InheritOnetimeChanges(models.Model):
    _inherit = 'hr.employee'

    hr_newsness = fields.One2many('newness.changes.lines', 'employee_id')

    def get_newness(self, code, p_pdo):
        if p_pdo == '1':
            p_pdo = '1st'
        elif p_pdo == '2':
            p_pdo = '2nd'

        newness = self.hr_newsness.filtered(lambda x: x.name.code == code and x.pdo == p_pdo and x.state_newness == 'running')

        total = 0.0
        for new in newness:
            total += new.amount

        return total

    def calculate_isr(self):
        minimum_scale = {
            'percentage': 0.15,
            'amount': 416220.01,
            'valueToAdd': 0.00
        }
        medium_scale = {
            'percentage': 0.20,
            'amount': 624329.01,
            'valueToAdd': 31216.00
        }
        maximum_scale = {
            'percentage': 0.25,
            'amount': 867123.01,
            'valueToAdd': 79776.00
        }
        # First payslip
        payslip = self.env['hr.payslip'].search([('employee_id', '=', self.id),
                                                 ('payment_period', '=', '1')])
        incen = payslip.line_ids.filtered(lambda x: x.code == 'INCEN')[-1:].amount
        other_incomes = payslip.line_ids.filtered(lambda x: x.code == 'OIN')[-1:].amount
        gasoline = payslip.line_ids.filtered(lambda x: x.code == 'COMB')[-1:].amount
        commissions = payslip.line_ids.filtered(lambda x: x.code == 'CO')[-1:].amount
        extra_hours = payslip.line_ids.filtered(lambda x: x.code == 'HE')[-1:].amount
        salary_tmp = payslip.line_ids.filtered(lambda x: x.code == 'SUEL')[-1:].amount
        salary = payslip.line_ids.filtered(lambda x: x.code == 'BASIC')[-1:].amount

        # Second payslip

        payslip_2 = self.env['hr.employee'].search([('id', '=', self.id)]).hr_newsness.\
            filtered(lambda x: x.pdo == '2nd' and x.state_newness == 'running')
        incen_2 = payslip_2.filtered(lambda x: x.name.code == 'incen')[-1:].amount
        other_incomes_2 = payslip_2.filtered(lambda x: x.name.code == 'oin')[-1:].amount
        gasoline_2 = payslip_2.filtered(lambda x: x.name.code == 'comb')[-1:].amount
        commissions_2 = payslip_2.filtered(lambda x: x.name.code == 'co')[-1:].amount
        extra_hours_2 = payslip_2.filtered(lambda x: x.name.code == 'he')[-1:].amount
        salary_tmp_2 = payslip_2.filtered(lambda x: x.name.code == 'suel')[-1:].amount

        for_add = other_incomes + other_incomes_2 + incen + incen_2 + gasoline + gasoline_2 + commissions + \
                  commissions_2 + extra_hours + extra_hours_2

        if not salary:
            sfs_1 = salary_tmp * 3.04 / 100
            afp_1 = salary_tmp * 2.87 / 100
            sfs_2 = salary_tmp_2 * 3.04 / 100
            afp_2 = salary_tmp_2 * 2.87 / 100
            salary_cot_1 = (salary_tmp - sfs_1 - afp_1)
            salary_cot_2 = (salary_tmp_2 - sfs_2 - afp_2)
            salary_cot = salary_cot_1 + salary_cot_2 + for_add
        else:
            sfs = salary * 3.04 / 100
            afp = salary * 2.87 / 100
            salary_cot = (salary - sfs - afp) + for_add

        annual_salary = salary_cot * 12

        isr = 0.0
        for row in payslip:
            if minimum_scale['amount'] <= annual_salary < medium_scale['amount']:

                excedent = annual_salary - minimum_scale['amount']
                percentage = excedent * minimum_scale['percentage']
                suma = percentage + minimum_scale['valueToAdd']
                isr = suma / 12

            elif medium_scale['amount'] <= annual_salary < maximum_scale['amount']:

                excedent = annual_salary - medium_scale['amount']
                percentage = excedent * medium_scale['percentage']
                suma = percentage + medium_scale['valueToAdd']
                isr = suma / 12

            elif annual_salary >= maximum_scale['amount']:

                excedent = annual_salary - maximum_scale['amount']
                percentage = excedent * maximum_scale['percentage']
                suma = percentage + maximum_scale['valueToAdd']
                isr = suma / 12

        isr_to_discount = isr * -1

        return isr_to_discount
