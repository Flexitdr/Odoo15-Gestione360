# -*- coding: utf-8 -*-
{
    'name': "Commission By Payment For ESD" ,

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ESD GROUP",
    'website': "http://www.grupoesd.com.do",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly

    'depends': ['sale_management', 'esd_sale_management'],


    # always loaded
    'data': [
        'data/groups.xml',
        'data/ir_cron.xml',
        'data/esd_commisions_required.xml',
        'reports/commissions.xml',
        # 'reports/commissions_by_user.xml',
        'security/ir.model.access.csv',
        'views/profile_commission_view.xml',
        'views/commission_pay_view.xml',
        'views/commission_line_view.xml',
        'views/account_journal_view.xml',
        'views/product_template_view.xml'
    ],
}
