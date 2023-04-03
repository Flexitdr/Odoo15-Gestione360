# -*- coding: utf-8 -*-
# from odoo import http


# class EsdSaleManagement(http.Controller):
#     @http.route('/esd_sale_management/esd_sale_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/esd_sale_management/esd_sale_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('esd_sale_management.listing', {
#             'root': '/esd_sale_management/esd_sale_management',
#             'objects': http.request.env['esd_sale_management.esd_sale_management'].search([]),
#         })

#     @http.route('/esd_sale_management/esd_sale_management/objects/<model("esd_sale_management.esd_sale_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('esd_sale_management.object', {
#             'object': obj
#         })
