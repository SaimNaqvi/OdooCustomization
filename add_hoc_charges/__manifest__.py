{
    "name": "Add hoc charges",

    "author": "NeoED Technologies",
    "category": "Accounts",

    "license": "OPL-1",

    "version": "15.0.1",

    "depends": [
        'sale_subscription',
        
        # 'account_accountant',
        # 'account'
        # 'account_accountant',
    ],
    'sequence': -100,

    "data": [
        'security/ir.model.access.csv'
        'views/add_hoc_charges.xml',
        'views/add_hoc_bill_chrages.xml',
    ],
    "images": [],
    "auto_install": False,
    "application": True,
    "installable": True,
    # "price": "60",
    # "currency": "EUR",
}
