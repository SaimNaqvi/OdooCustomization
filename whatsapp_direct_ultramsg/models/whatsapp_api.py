import requests
from odoo import models, fields, api
from odoo.exceptions import UserError


class WhatsappConfig(models.Model):
    _name = 'whatsapp.config'
    _description = 'WhatsApp Configuration'

    name = fields.Char(default='WhatsApp Settings')
    instance_id = fields.Char(required=True)
    token = fields.Char(required=True)

    @api.model
    def get_config(self):
        config = self.search([], limit=1)
        if not config:
            raise UserError("Please configure WhatsApp API settings.")
        return config

    def send_whatsapp_message(self, phone, message):
        url = f"https://api.ultramsg.com/{self.instance_id}/messages/chat"
        payload = {
            'token': self.token,
            'to': phone,
            'body': message,
        }
        response = requests.post(url, data=payload)
        return response.json()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # def action_send_whatsapp(self):
    #     config = self.env['whatsapp.config'].get_config()
    #     for partner in self:
    #         if partner.mobile:
    #             message = f"Hello {partner.name}, this is a test WhatsApp message from Odoo."
    #             result = config.send_whatsapp_message(partner.mobile, message)
    #             if result.get('sent'):
    #                 msg = 'Message sent successfully'
    #             else:
    #                 msg = f"Failed: {result}"
    #         else:
    #             msg = 'No mobile number found'
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': 'WhatsApp',
    #             'message': msg,
    #             'type': 'info',
    #         }
    #     }
    def action_send_whatsapp(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send WhatsApp Message',
            'res_model': 'whatsapp.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_message': f"Hello {self.name}, please find attached message.",
            }
        }

