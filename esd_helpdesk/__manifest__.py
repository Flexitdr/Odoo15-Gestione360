# -*- coding: utf-8 -*-
{
    'name': "ESD Helpdesk",
    'summary': """""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Group ESD",
    'website': "https://grupoesd.do/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'helpdesk_mgmt'],
    'data': [
        'views/categories_view.xml',
        'views/ticket_view.xml',
        'views/tags_view.xml',
        # 'views/ticket_tags_view.xml',
        # 'security/ir.model.access.csv',
    ],
    'demo': [],
    # 'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto-install': True,
}