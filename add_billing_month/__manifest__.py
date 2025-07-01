{
    'name': 'Add Billing Month Field',
    'version': '1.0.0',
    'category': 'Sale',
    'sequence': 0,
    'summary': 'To add the billing month field in fee manager - subscription',
    'description': """Adding the field named billing month - Schola Nova""",
    # 'website': '',
    'depends': [
        'sale_subscription',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/billing_month_field_view.xml'
    ],
    'demo': [],
    'application': True,
    'installation': True,
    # 'assets': {},
    'license': 'LGPL-3'
}
