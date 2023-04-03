
from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class SubscriptionPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "subscription_count" in counters:
            subscriptions = request.env["subscription.package"]
            subscription_count = (
                subscriptions.search([])
                if subscriptions.check_access_rights("read", raise_exception=False)
                else 0
            )

            values["subscription_count"] = len(subscription_count.ids)
        return values

    @http.route(
        ["/my/subscriptions", "/my/subscriptions/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_subscriptions(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        subscriptions = request.env["subscription.package"]
        # Avoid error if the user does not have access.
        if not subscriptions.check_access_rights("read", raise_exception=False):
            return request.redirect("/my")

        domain = []

        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
            "stage": {"label": _("Stage"), "order": "stage_id"},
            "update": {
                "label": _("Last Stage Update"),
                "order": "last_stage_update desc",
            },
        }
        searchbar_filters = {"all": {"label": _("All"), "domain": []}}
        for stage in request.env["subscription.package.stage"].search([]):
            searchbar_filters.update(
                {
                    str(stage.id): {
                        "label": stage.name,
                        "domain": [("stage_id", "=", stage.id)],
                    }
                }
            )

        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # default filter by value
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]

        # count for pager
        subscriptions_count = subscriptions.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/subscriptions",
            url_args={},
            total=subscriptions_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        # tickets = subscriptions_count.search(
        #     domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        # )
        values.update(
            {
                "date": date_begin,
                "subscriptions": subscriptions_count,
                "page_name": "subscription",
                "pager": pager,
                "default_url": "/my/subscriptions",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
            }
        )
        return request.render("esd_subscription_package.portal_my_subscriptions", values)

    @http.route(
        ["/my/subscription/<int:subscription_id>"], type="http", auth="public", website=True
    )
    def portal_my_subscription(self, subscription_id=None, access_token=None, **kw):
        try:
            subs_sudo = self._document_check_access(
                "subscription.package", subscription_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._subscription_get_page_view_values(subs_sudo, **kw)
        return request.render("esd_subscription_package.portal_subscriptions_page", values)

    def _subscription_get_page_view_values(self, subscription, **kwargs):
        closed_stages = request.env["subscription.package.stage"].search(
            [("closed", "=", True)]
        )
        values = {
            "page_name": "subscription",
            "ticket": subscription,
            "closed_stages": closed_stages,
        }

        if kwargs.get("error"):
            values["error"] = kwargs["error"]
        if kwargs.get("warning"):
            values["warning"] = kwargs["warning"]
        if kwargs.get("success"):
            values["success"] = kwargs["success"]

        return values
