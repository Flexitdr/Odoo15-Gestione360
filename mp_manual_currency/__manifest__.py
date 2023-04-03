# -*- coding: utf-8 -*-
{
    'name': "mp_manual_currency",
    'summary': """Cambiar tasa de moneda manualmente""",
    'description': """Cambiar tasa de moneda manualmente""",
    'author': "MERPLUS, SRL",
    'website': "http://www.mer.plus",
    'license': 'LGPL-3',
    'category': 'Accounting',
    'version': '0.1',
    "depends" : ['base','account','purchase','sale_management','stock'],
    'data': [
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ],
}
