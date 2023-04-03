# -*- coding: utf-8 -*-
# from odoo import http


# class PrinterMrp(http.Controller):
#     @http.route('/printer_mrp/printer_mrp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/printer_mrp/printer_mrp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('printer_mrp.listing', {
#             'root': '/printer_mrp/printer_mrp',
#             'objects': http.request.env['printer_mrp.printer_mrp'].search([]),
#         })

#     @http.route('/printer_mrp/printer_mrp/objects/<model("printer_mrp.printer_mrp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('printer_mrp.object', {
#             'object': obj
#         })
