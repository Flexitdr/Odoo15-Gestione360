# -*- coding: utf-8 -*-
{
    'name': "Recurrence and Fee",

    'summary': """

       """,

    'description': """

    """,

    'author': "ESD GROUP",
    'website': "http://www.grupoesd.com.do",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly

    'depends': ['esd_subscription_package', 'esd_sale_management', 'sale', 'account'],

    'data': [
        'data/recurrence.xml',
        'data/create_recurrence.xml',
        'views/account_move_views.xml',
        # 'reports/recurrence_sale_report.xml'
    ],

    'auto-install': True

}
