# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api, _
import xlsxwriter


class ReportTss(models.Model):
    _name = 'report.tss.form'
    _order = 'id desc'

    name = fields.Char(string='Name', required=True)
    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    payment_period = fields.Many2one('hr.payslip.run', required=True)
    file_to_report = fields.Binary(string='File to Report')
    file_name = fields.Char(string='File Name')
    is_visible = fields.Boolean(string="Visible", default=False)

    def generate_report_xls(self, rec):

        employee_list = ()
        emp = list(employee_list)
        report_name = rec.name
        workbook = xlsxwriter.Workbook('tmp/{}.xlsx'.format(report_name))
        worksheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'bold': True, 'bg_color': 'yellow'})
        worksheet.write(0, 0, 'Empleado', cell_format)
        worksheet.write(0, 1, 'Documento', cell_format)

        salary_rules = self.env['hr.salary.rule'].search([('appears_on_tss', '=', True), ('show_in_header', '=', True)])
        count = 2
        for i in range(len(salary_rules)):
            worksheet.write(0, count, salary_rules[i].name, cell_format)

            # if i == len(salary_rules) - 1:
            #     worksheet.write(0, count, 'TOTAL COTIZABLE', cell_format)
            #     worksheet.write(0, count + 1, 'TOTAL OTROS INGRESOS', cell_format)
            count += 1

        payslip = self.env['hr.payslip.run'].search([('id', '=', rec.payment_period.id)])
        # OJO
        slip_ids_report = payslip.slip_ids.filtered(lambda x: x.date_from >= rec.date_from and x.date_to <= rec.date_to)

        for e in slip_ids_report.employee_id:
            payslips_emp = slip_ids_report.filtered(lambda x: x.employee_id.id == e.id)

            for p in payslips_emp:
                rules = p.line_ids.salary_rule_id.filtered(lambda x: x.appears_on_tss is True)
                rules_sum = rules.filtered(lambda x: x.where_sum_id)
                list_2 = []
                for r in rules:
                    for_tss = p.line_ids.filtered(lambda x: x.code == r.code)
                    value_add = 0.00
                    if r.show_in_header is True:
                        if for_tss.code == 'BASIC':
                            value_add += (for_tss.amount / 2)
                            for val in rules_sum:
                                for_add = p.line_ids.filtered(lambda x: x.code == val.code)
                                if val.where_sum_id.code == r.code:
                                    value_add += for_add.amount
                            list_2.append(value_add)
                        else:
                            value_add += for_tss.amount
                            for val in rules_sum:
                                for_add = p.line_ids.filtered(lambda x: x.code == val.code)
                                if val.where_sum_id.code == r.code:
                                    value_add += for_add.amount
                            list_2.append(value_add)

                list_1 = [p.employee_id.name,
                          p.employee_id.identification_id,]
                res = [*list_1, *list_2]
                emp.append(res)
                employee_list = tuple(emp)

        row = 1
        col = 0

        for i in employee_list:
            for val in range(len(i)):
                worksheet.write(row, col, i[val])
                col += 1
            row += 1
            col = 0

        workbook.close()
        with open(workbook.filename, "rb") as file:
            file_base64 = base64.b64encode(file.read())

        rec.file_name = rec.name + '.xlsx'
        rec.file_to_report = file_base64
        rec.is_visible = True

    @api.model
    def create(self, vals):
        rec = super(ReportTss, self).create(vals)
        self.generate_report_xls(rec)
        return rec

