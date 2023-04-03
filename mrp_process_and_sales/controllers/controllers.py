# -*- coding: utf-8 -*-
# from odoo import http


# class MrpProcessAndSales(http.Controller):
#     @http.route('/mrp_process_and_sales/mrp_process_and_sales', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_process_and_sales/mrp_process_and_sales/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_process_and_sales.listing', {
#             'root': '/mrp_process_and_sales/mrp_process_and_sales',
#             'objects': http.request.env['mrp_process_and_sales.mrp_process_and_sales'].search([]),
#         })

#     @http.route('/mrp_process_and_sales/mrp_process_and_sales/objects/<model("mrp_process_and_sales.mrp_process_and_sales"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_process_and_sales.object', {
#             'object': obj
#         })
