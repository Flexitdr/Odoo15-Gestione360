# -*- coding: utf-8 -*-
{
    'name': "HR Custom Fields",

    'summary': """
        Add some field for Humans Resources""",

    'description': """
        Add some field for Humans Resources
    """,

    'author': "Group ESD",
    'website': "https://grupoesd.do/",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_payroll_account_community'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}