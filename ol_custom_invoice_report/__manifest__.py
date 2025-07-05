# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Custom Invoice Report",

    "author": "Saim | NEOED",
    "category": "Accounts",

    "license": "OPL-1",

    "version": "15.0.1",

    "depends": [
        'account_accountant',
        'account',


    ],
    'sequence': -1000,

    "data": [
        'views/wizard.xml',
        'security/ir.model.access.csv'
        # 'reports/sale_agrement.xml',
        # 'reports/fee_challan.xml',

    ],
    "images": [],
    "auto_install": False,
    "application": True,
    "installable": True,
    # "price": "60",
    # "currency": "EUR",
}
