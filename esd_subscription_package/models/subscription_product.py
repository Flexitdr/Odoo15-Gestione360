from odoo import _, api, models, fields, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, Warning


class ProductTemplate(models.Model):
    _inherit = "product.template"

    subscription_plan_product_id = fields.Many2one('product.product', domain="[('is_subscription', '=', True)]",
                                                   string='Subscription Product')

    visit_plan_product_id = fields.Many2one('product.product', domain="[('is_subscription', '=', True)]",
                                            string='Visit Product')