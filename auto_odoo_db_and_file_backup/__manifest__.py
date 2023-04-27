# -*- coding: utf-8 -*-
#odoo15
{
    'name': "Automatic Backup (Google Drive, Dropbox, Amazon S3, FTP, SFTP, Local)",
	'category': 'Extra Tools',
	'version': '1.0', 
	
    'summary': 'Automatic Backup -(Google Drive, Dropbox, Amazon S3, FTP, SFTP, Local)',
    'description': "Automatic Backup -(Google Drive, Dropbox, Amazon S3, FTP, SFTP, Local)",
	'license': 'OPL-1',
    'price': 29.29,
	'currency': 'USD',
	
	'author': "Icon TechSoft Pvt. Ltd.",
    'website': "https://icontechnology.co.in",
    'support':  'team@icontechnology.in',
    'maintainer': 'Icon TechSoft Pvt. Ltd.',
	
 	'images': ['static/description/auto-backup_odoo-v15.gif'],
	
    # any module necessary for this one to work correctly
    'depends': ['base','google_drive','mail'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/auto_backup_mail_templates.xml',
        'data/data.xml',
    ],
    'installable': True,
    'application': True,
}
