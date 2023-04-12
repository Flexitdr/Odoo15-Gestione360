# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Recurring Invoice',
    'version': '1.0',
    'sequence': 1,
    'category': 'Accounting',
    'description':
        """
 This Module add below functionality into odoo

        1.Recurring Invoice\n

Odoo application will re-create invoice based on your configuration of Recurring Invoice. System will automatically generates copy of Invoice based on your configuration. You can also set a user who will be notify via email when invoice is recurring and you can also set stop date from onward that date recurring of invoice will be stopped.

- System will automatically generates copy of Invoice based on your configuration
- Set which Invoice you want to re-occur
- When you select Invoice all the invoice lines of that invoice will be loaded automatically,
  You can also modify it as per your need
- Select time interval of re-occurring invoice, such as every 1 day, every 2 weeks, every 1 month etc
- Set a user who will be notify via email when invoice is re-occurred
- Set stop date so onward that date re-occurring of invoice will be stopped


odoo app for Recurring Invoice, Subscription Invoice,Recurring Invoice Subscription,Recurring Invoice, Auto Recurring Invoice,Recurring Invoice notification, Recurring Invoice auto, Recurring Invoice stop date

    """,
    'summary': 'odoo app for Recurring Invoice, Subscription Invoice,Recurring Invoice Subscription,Recurring Invoice, Auto Recurring Invoice,Recurring Invoice notification, Recurring Invoice auto,Recurring Invoice stop date',
    'depends': ['account','sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/template_recurring_invoice.xml',
        'data/cron_recurring_invoice.xml',
        'views/recurring_invoice_setting_views.xml'
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':15.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
