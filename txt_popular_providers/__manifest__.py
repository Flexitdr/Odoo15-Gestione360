# -*- coding: utf-8 -*-
{
    'name': "Txt Providers",
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
        'security/ir.model.access.csv',
        'views/txt_providers.xml',
        'views/providers.xml',
        'views/config.xml',
        'wizard/txt_providers_wizard_view.xml',
    ],
    'demo': [],
    # 'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}