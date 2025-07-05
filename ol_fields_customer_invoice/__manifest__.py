# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Add fields in invoices',
    'author':'Saim Naqvi | NeoEd Technologies',
    'version': '1.0',
    'sequence':-110,
    'summary': 'Add fields in invoices',
    'description': """Add fields in invoices""",
    'depends': ['account','ol_custom_school_arrears'],
    'data': [
        'views/view.xml',
        ],
    'demo': [],
    'installable': True,
    'assets': {},
    'application':True,
    'license': 'LGPL-3',
}
