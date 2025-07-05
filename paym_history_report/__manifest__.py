# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Payment history (fee challan)",

    "author": "NeoEd Technologies",
    "developer": "Saim Naqvi",
    "category": "",

    "license": "OPL-1",

    "version": "15.0.1",

    "depends": [
        'account_accountant',
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/payment_history.xml",
        "views/late_fee_scheduler_action.xml",
    ],

    "auto_install": False,
    "application": True,
    "installable": True,

}
