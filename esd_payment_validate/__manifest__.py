# -*- coding: utf-8 -*-
{
    'name': "ESD Payment Validate",

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


    'depends': ['account'],

    'data': [
        'data/payment_validate.xml',
        'security/ir.model.access.csv',
        'views/azul_books_views.xml'

    ],

    'auto-install': True

}
