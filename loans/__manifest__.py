# -*- coding: utf-8 -*-
{
    'name': "Loans",
    'summary': """""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Group ESD",
    'website': "https://grupoesd.do/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail'],
    'data': [
        'views/collaborator_loans.xml',
        'views/configuration.xml',
        'security/ir.model.access.csv',
        'wizard/collaborator_loans_wizard.xml',
        'views/interest_rate.xml',
        # 'security/security.xml',
        # 'views/azul_codes.xml',
        # 'views/res_partner_codes.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}