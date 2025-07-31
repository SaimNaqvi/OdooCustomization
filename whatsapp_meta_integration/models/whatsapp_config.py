from odoo import models, fields


class WhatsAppConfig(models.Model):
    _name = 'whatsapp.config'
    _description = 'WhatsApp Configuration'

    access_token = fields.Char("Access Token", required=True)
    phone_number_id = fields.Char("Phone Number ID", required=True)
    whatsapp_business_id = fields.Char("Business Account ID")
    default_sender_name = fields.Char("Sender Name")
    is_active = fields.Boolean("Active", default=True)
