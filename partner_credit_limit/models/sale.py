# See LICENSE file for full copyright and licensing details.


from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    #@api.multi
    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        
        if partner.block_credit:
            msg = 'El cliente %s tiene el crédito bloqueado ' % (self.partner_id.name)
            raise UserError(_('La orden no puede ser confirmada. \n' + msg))

        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:
            """
            moveline_obj = self.env['account.move.line']
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('account_id.user_type_id.name', 'in',
                  ['Receivable', 'Payable'])]
            )
            confirm_sale_order = self.search([('partner_id', '=', partner.id),
                                              ('state', '=', 'sale')])
            debit, credit = 0.0, 0.0
            amount_total = 0.0
            for status in confirm_sale_order:
                amount_total += status.amount_total
            for line in movelines:
                credit += line.credit
                debit += line.debit
            partner_credit_limit = (partner.credit_limit - debit) + credit
            available_credit_limit = \
                ((partner_credit_limit -
                  (amount_total - debit)) + self.amount_total)
            """
            amount_total = self.amount_total           

            invoice_id = self.env['account.move'].search([
                                 ('partner_id', '=', partner.id),('state','=','open')])
                             
            for i in invoice_id:               
                amount_total += i.residual_signed
            
            available_credit_limit = (partner.credit_limit - amount_total) 
            
            if amount_total  > partner.credit_limit:
                if not partner.over_credit:
                    msg = 'Ha sobre pasado el límite permitido' \
                          ' Cantidad = %s \nCheques "%s" Facturas or Créditos ' \
                          'Límites ' % (available_credit_limit,
                                       self.partner_id.name)
                    raise UserError(_('La orden no puede ser confirmada. '
                                      ' \n' + msg))
                #partner.write({'credit_limit': credit - debit + self.amount_total})
            return True
    
    #@api.multi
    def check_due_invoice(self):
        today = datetime.today()        
        partner = self.partner_id        
        allow_days = self.partner_id.allow_days
        payment_term = False

        invoice_id = self.env['account.move'].search([
            ('partner_id', '=', partner.id),('state','=','open')])
        
        terms = self.env['account.payment.term.line'].search([
            ('payment_id', '=', partner.property_payment_term_id.id)])

        for i in invoice_id:
            date_invoice = datetime.strptime(str(i.date_invoice),'%Y-%m-%d')
            delta = today - datetime.strptime(str(i.date_invoice),'%Y-%m-%d') 
            
            for tt in terms:
                if not partner.overdue_bills:
                    payment_term = True
                    if delta.days > tt.days + allow_days:
                        msg = 'EL cliente posee la siguiente factura %s vencida de fecha %s ' % (i.reference,datetime.strptime(str(i.date_invoice),'%Y-%m-%d'))
                        raise UserError(_('La orden no puede ser confirmada. '
                                        ' \n' + msg))
            
            if not payment_term and not partner.overdue_bills:
                msg = 'El cliente no tiene definido el plazo de pago  ' 
                raise UserError(_('La orden no puede ser confirmada. '
                                        ' \n' + msg))

        return True
    
    #@api.multi
    def _action_confirm(self):        
        for order in self:            
            order.check_limit()
            order.check_due_invoice()
        res = super(SaleOrder, self)._action_confirm()
        return res

    """
    @api.constrains('amount_total')
    def check_amount(self):
        for order in self:      
            order.check_due_invoice()      
            if order.state != 'draft':
                order.check_limit()
                order.check_due_invoice()
    """
