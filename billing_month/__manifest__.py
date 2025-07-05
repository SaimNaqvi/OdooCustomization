{
    'name': 'Add Billing Month Field Osama',
    'author':'Osama',
    'version': '1.0.0',
    'category': 'Sale',
    'sequence': 0,
    'summary': 'To add the billing month field in invoices - ',
    'description': """Adding the field named billing month - Schola Nova""",
    # 'website': '',
    'depends': [
        'sale_subscription',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/billingMonth.xml',
    ],
    'demo': [],
    'application': True,
    'installation': True,
    # 'assets': {},
    'license': 'LGPL-3'
}
