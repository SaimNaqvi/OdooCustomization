# -*- coding: utf-8 -*-


{
    'name': 'Bulk Change Invoice Due Date',

    "author": "Usama Shahid | Odolution",
    'version': '0.1',
    'category': 'Invoice Customization',
    'sequence': 95,
    'summary': 'Implementation of bulk change due date.',
    'description': "Implementation of bulk change due date.",
    'website': '',
    'images': [
    ],
    'depends': ["account",
    ],
    'data': [
        
        "views/view.xml",
        "security/ir.model.access.csv"
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
    ],
    'license': 'LGPL-3',
}
