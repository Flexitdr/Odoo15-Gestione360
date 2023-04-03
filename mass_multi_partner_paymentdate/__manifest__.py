# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': "Mass Multi Partner Payment Date",
    'version': '15.0.0.1',
    'category': 'Accounting',
    'license': 'Other proprietary',
    'summary': "Geminate comes with a feature of mass multiple partner payment date where we can select multiple invoices / bills which have different payment dates configured on individual records. In case, if there is no payment date configured on invoice/bill then priority given to payment date from wizard for mass payment registration.",
    'description': """Geminate comes with a feature of mass multiple partner payment date where we can select multiple invoices / bills which have different payment dates configured on individual records. In case, if there is no payment date configured on invoice/bill then priority given to payment date from wizard for mass payment registration.
    """,
    'author': "Geminate Consultancy Services",
    'website': 'http://www.geminatecs.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        "views/account_date_view.xml",
        "wizard/account_paymenty_date_view.xml",
    ],

    "images" :  ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 79.99,
    'currency': 'EUR'
}
