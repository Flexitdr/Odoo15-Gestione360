# -*- coding: utf-8 -*-
{
    'name': "ESD Onetime Changes",
    'summary': """""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Group ESD",
    'website': "https://grupoesd.do/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hr_payroll_community', 'hr_custom_fields'],
    'data': [
        'views/onetime_changes_view.xml',
        'views/newness_changes_view.xml',
        'views/upload_file_view.xml',
        'views/requests_newness_view.xml',
        'security/ir.model.access.csv',
        'wizard/requests_refuse_wizard.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}