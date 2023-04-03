# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeAssignmentMrp(http.Controller):
#     @http.route('/employee_assignment_mrp/employee_assignment_mrp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_assignment_mrp/employee_assignment_mrp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_assignment_mrp.listing', {
#             'root': '/employee_assignment_mrp/employee_assignment_mrp',
#             'objects': http.request.env['employee_assignment_mrp.employee_assignment_mrp'].search([]),
#         })

#     @http.route('/employee_assignment_mrp/employee_assignment_mrp/objects/<model("employee_assignment_mrp.employee_assignment_mrp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_assignment_mrp.object', {
#             'object': obj
#         })
