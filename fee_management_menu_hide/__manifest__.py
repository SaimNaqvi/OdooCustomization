{
    'name': 'Fee Management Menu Hide',
    'version': '1.0.0',
    'category': 'Productivity',
    'sequence': 0,
    'summary': 'To Hide Fee Management Menuitems',
    'description': """Hiding Fee Management System Menuitems - Schola Nova""",
    # 'website': '',
    'depends': [
        'sale_subscription',
        'account_accountant',
        'account_followup'
    ],
    'data': [
        'views/fee_management_menuhide_view.xml'
    ],
    'demo': [],
    'application': True,
    'installation': True,
    # 'assets': {},
    'license': 'LGPL-3'
}
