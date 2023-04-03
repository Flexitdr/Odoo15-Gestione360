# -*- coding: utf-8 -*-
{
    'name': "ESD Sale Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Coway",
    'website': "http://www.coway.com.do",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fee.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/financing_plan.xml',
        'views/offer.xml',
        'views/res_partner.xml',
        'views/payment_bank.xml',
        'views/type_document.xml',
        'views/menus.xml',
        'reports/report_saleorder.xml',
        'views/account.xml',
        'views/sale_order_state_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
