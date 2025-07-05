{
    'name': 'WhatsApp Direct via Ultramsg',
    'version': '15.0.1.0',
    'category': 'Communication',
    'summary': 'Send WhatsApp messages directly via Ultramsg API',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_config_view.xml',
        'views/partner_whatsapp_button.xml',
        'views/whatsapp_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
}
