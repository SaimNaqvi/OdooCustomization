# -*- coding: utf-8 -*-

{
    'name': 'Classwise Report',
    'version': '1.0.0',
    'category': 'Report',
    'author':'Odoo mates',
    'sequence': -100,
    'summary': 'Classwise Report',
    'description': """Classwise report of students calculating total number of male and female students in each class, section and school """,
    'depends': ['ol_custom_invoice_report','account', 'son_accounting_menu','base'],
    'data': [
        'reports/ol_classwise_report_button.xml',
        'reports/ol_classwise_report_view.xml',
        'reports/ol_classwise_defaulter_report_button.xml',
        'reports/ol_defaulter_report_view.xml',
        'wizard/ol_classwise_report_wizard.xml',
        ],
    'demo': [],
    'application':True,
    'installable': True,
    'assets': {},
    #'post_init_hook': '_synchronize_cron',
    'license': 'LGPL-3',
}
