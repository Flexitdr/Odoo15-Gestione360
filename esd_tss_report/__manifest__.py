# -*- coding: utf-8 -*-
{
    'name': "ESD TSS Report",
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
        'views/appears_tss.xml',
        'views/report_tss.xml',
        'views/structure_salary.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}