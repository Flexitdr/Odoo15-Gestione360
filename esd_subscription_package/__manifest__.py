# -*- coding: utf-8 -*-

{
    'name': 'Subscription Management For ESD',
    'Version': '15.0.1.0.0',
    'summary': 'Subscription Package Management Module For Group ESD for it to work in the Dominican Republic',
    'description': 'Subscription Package Management Module For Group ESD for it to work in the Dominican Republic',
    'category': 'Sales',
    'author': 'Group ESD',
    'website': "https://grupoesd.do/",
    'depends': ['base', 'subscription_package', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/renew_subscription_mail_view.xml',
        'data/renew_subscription_mail_auto.xml',
        'data/esd_subscription_stage_data.xml',
        'data/esd_subscription_product.xml',
        'data/update_next_invoice_date.xml',
        'data/calculate_old_date.xml',
        'data/renew_subscription_plan.xml',
        'data/active_subscription_plan_by_payment.xml',
        'data/groups.xml',
        'views/subscripcion_package_view.xml',
        'views/renew_subscription_view.xml',
        'views/res_partner_view.xml',
        'views/subscription_portal_templates.xml',
        'views/subscription_payment_line_view.xml',
        'views/subscription_plan_view.xml',
        'views/subscription_product_view.xml',
        'views/visit_subscription_manager_views.xml'


    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
