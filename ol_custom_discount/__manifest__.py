# -*- coding: utf-8 -*-


{
    'name': 'Custom Discount',

    "author": "Usama Shahid | Odolution",
    'version': '0.1',
    'category': 'Invoice Customization',
    'sequence': 95,
    'summary': 'Implementation of Custom discount of specific requirements of lacas.',
    'description': "Implementation of Custom discount of specific requirements of lacas.",
    'website': '',
    'images': [
    ],
    'depends': ["account",'sale','product'
        
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
