# -*- coding: utf-8 -*-
# from odoo import http


# class EsdSubscriptionIntegrationSales(http.Controller):
#     @http.route('/esd_subscription_integration_sales/esd_subscription_integration_sales', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/esd_subscription_integration_sales/esd_subscription_integration_sales/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('esd_subscription_integration_sales.listing', {
#             'root': '/esd_subscription_integration_sales/esd_subscription_integration_sales',
#             'objects': http.request.env['esd_subscription_integration_sales.esd_subscription_integration_sales'].search([]),
#         })

#     @http.route('/esd_subscription_integration_sales/esd_subscription_integration_sales/objects/<model("esd_subscription_integration_sales.esd_subscription_integration_sales"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('esd_subscription_integration_sales.object', {
#             'object': obj
#         })
