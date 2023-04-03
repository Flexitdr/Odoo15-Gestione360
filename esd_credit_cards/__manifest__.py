# -*- coding: utf-8 -*-
{
    'name': "ESD Credit Cards",
    'summary': """""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Group ESD",
    'website': "https://grupoesd.do/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account'],
    'data': [
        'views/website_form.xml',
        'views/credit_cards.xml',
        'data/groups.xml',
        'security/ir.model.access.csv',
        'views/azul_codes.xml',
        'views/res_partner_codes.xml',
    ],
    'demo': [],
    # 'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}