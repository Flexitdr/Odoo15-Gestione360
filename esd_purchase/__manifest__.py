# -*- coding: utf-8 -*-
{
    'name': "ESD Purchase",
    'summary': """""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Group ESD",
    'website': "https://grupoesd.do/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'purchase'],
    'data': [
        'views/purchase_view.xml',
        'reports/purchase_template.xml',
        'reports/purchasequotation_template.xml',
        'views/comments_purchase_view.xml',
        'views/stamp_company_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    # 'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto-install': True,
}