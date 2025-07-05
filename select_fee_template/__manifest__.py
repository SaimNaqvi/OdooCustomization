{
    'name': 'Choose Fee Template',
    'version': '1.0.0',
    'category': 'Productivity',
    'sequence': 0,
    'summary': 'Select a fee template for student',
    'description': """Through this module we can select a fee template for a student - Schola Nova""",
    # 'website': '',
    'depends': [
        'sale_subscription',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_subscription_template_wizard.xml',
    ],
    'demo': [],
    'application': True,
    'installation': True,
    'license': 'LGPL-3'
}
