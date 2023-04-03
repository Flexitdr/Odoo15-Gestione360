from odoo import _, api, models, fields, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, Warning


class ResPartner(models.Model):

    _inherit = 'res.partner'

    partner_subs_count = fields.One2many('subscription.package', 'id')

    subs_ticket_count = fields.Integer(
        compute="_compute_subscription_count", string="Subscription count"
    )

    subs_count_active_count = fields.Integer(
        compute="_compute_subscription_count", string="Subscription active count"
    )

    subs_count_string = fields.Char(
        compute="_compute_subscription_count", string="Subscriptions"
    )

    def _compute_subscription_count(self):
        for record in self:
            subs_ids = self.env["subscription.package"].search(
                [("partner_id", "child_of", record.id)]
            )
            record.subs_ticket_count = len(subs_ids)
            record.subs_count_active_count = len(
                subs_ids.filtered(lambda subs: not subs.current_stage == 'closed')
            )
            count_active = record.subs_count_active_count
            count = record.subs_ticket_count
            record.subs_count_string = "{} / {}".format(count_active, count)

    def action_view_subs_view(self):
        return {
            "name": self.name,
            "view_mode": "tree,form",
            "res_model": "subscription.package",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "child_of", self.id)],
            "context": self.env.context,
        }
