# -*- coding: utf-8 -*-
{
    'name': "Txt Payroll",
    'summary': """""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Group ESD",
    'website': "https://grupoesd.do/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr_payroll_community'],
    'data': [
        'security/ir.model.access.csv',
        'views/txt_payroll.xml',
        # 'views/providers.xml',
        'views/config.xml',
        'wizard/txt_payroll_wizard_view.xml',
    ],
    'demo': [],
    # 'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}