from odoo import models, fields, api
from datetime import datetime
import base64
from xlrd import open_workbook
from odoo.exceptions import UserError


class UploadFile(models.Model):
    _name = 'upload.file'
    _order = 'id desc'

    date = fields.Date(string='Fecha de subida', required=True, default=datetime.today())
    file = fields.Binary(string='Subir archivo', required=True)
    file_name = fields.Char('File Name')
    responsible = fields.Many2one('hr.employee', readonly=True,
                                  default=lambda self: self.env.user.employee_id and self.env.user.employee_id.id or False)

    def create_requests(self, rec):

        file_data = base64.b64decode(rec.file)
        book = open_workbook(file_contents=file_data)

        row = 4
        column = 1
        sheet = book.sheet_by_index(0)

        while True:
            try:

                user = str(sheet.cell_value(row, column))
                pdo = sheet.cell_value(row, column + 1)
                employee = self.env['hr.employee'].search([('code', '=', user)]).id
                count = 0
                newness_lines = []
                for new_line in sheet.cell_value(row, column + 2).split(',' or False):

                    newness = sheet.cell_value(row, column + 2).split(',' or False)[count]
                    amounts = sheet.cell_value(row, column + 3).split(',' or False)[count]
                    start_dates = sheet.cell_value(row, column + 4).split(',' or False)[count]
                    end_dates = sheet.cell_value(row, column + 5).split(',' or False)[count]
                    # if start_dates and end_dates == '':
                    #     raise UserError('You can not leave any empty date.')
                    newness_id = self.env['newness.changes'].search([('code', '=', newness)], limit=1).id
                    newness_lines.append((0, 0, {
                        'newness': newness_id,
                        'amount': amounts,
                        'start_date': datetime.strptime(start_dates, '%d/%m/%Y'),
                        'end_date': datetime.strptime(end_dates, '%d/%m/%Y')
                    }))
                    count += 1

                vals = {
                    'date': rec.date,
                    'employee': employee,
                    'pdo': pdo,
                    'newness_id': newness_lines
                }

                row = row + 1

                self.env['requests.newness'].create(vals)
            except IndexError:
                break

    @api.model
    def create(self, vals):
        rec = super(UploadFile, self).create(vals)
        self.create_requests(rec)
        return rec
