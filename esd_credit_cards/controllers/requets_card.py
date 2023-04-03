from odoo import http
from odoo.http import request


class CreditCards(http.Controller):

    @http.route('/register/card', type='http', website=True, auth='public')
    def credit_cards(self, **kw):
        return http.request.render('esd_credit_cards.register_credit_cards', {})

    @http.route('/create/customer/card', type='http', website=True, auth='public')
    def create_card_execution(self, **kw):
        card = kw['number_card']
        card_mask = card[-4:].rjust(len(card), '*')
        kw['number_card'] = card_mask
        kw['storage_card'] = card
        request.env['credit.cards'].sudo().create(kw)
        return request.render('esd_credit_cards.register_thanks', {})
