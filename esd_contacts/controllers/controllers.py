# -*- coding: utf-8 -*-
# from odoo import http


# class EsdContacts(http.Controller):
#     @http.route('/esd_contacts/esd_contacts', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/esd_contacts/esd_contacts/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('esd_contacts.listing', {
#             'root': '/esd_contacts/esd_contacts',
#             'objects': http.request.env['esd_contacts.esd_contacts'].search([]),
#         })

#     @http.route('/esd_contacts/esd_contacts/objects/<model("esd_contacts.esd_contacts"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('esd_contacts.object', {
#             'object': obj
#         })
