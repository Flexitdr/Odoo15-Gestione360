from odoo import _, api, models, fields, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, Warning


class SubscriptionPackageStage(models.Model):
    _inherit = "subscription.package.stage"

    category = fields.Selection(selection_add = [('approved', 'Approved'), ('expiration', 'Expiration'),
                                                 ('cancel', 'Cancel'), ], readonly=False, default='draft')