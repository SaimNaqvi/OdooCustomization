{
    "name": "WhatsApp Meta Integration",
    "version": "17.0.1.0.0",
    "depends": ["base", "mail", "contacts"],
    "category": "Tools",
    "summary": "Send WhatsApp messages via Meta API and log in chatter",
    "description": "WhatsApp integration using Meta's Cloud API",
    "data": [
        "security/ir.model.access.csv",
        "views/whatsapp_config_views.xml",
        "views/send_whatsapp_wizard_views.xml",
        "views/res_partner_button.xml"
    ],
    'images': ['static/description/icon.png'],
    "installable": True,
    "application": True,
}
