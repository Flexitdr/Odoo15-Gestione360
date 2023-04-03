# -*- coding: utf-8 -*-
{
    'name': "ESD Account Payment",
    'summary': """""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Group ESD",
    'website': "https://grupoesd.do/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account_payment', 'gts_multiple_invoice_payment_plus'],
    'data': [
        'views/account_payment_views.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}