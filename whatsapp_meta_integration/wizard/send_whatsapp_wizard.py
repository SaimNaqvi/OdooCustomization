from odoo import models, fields, api
from odoo.exceptions import UserError
import requests


class WhatsAppSendWizard(models.TransientModel):
    _name = 'whatsapp.send.wizard'
    _description = 'Send WhatsApp Message'

    partner_id = fields.Many2one('res.partner', string="Recipient", required=True)
    mobile = fields.Char(related='partner_id.mobile', required=True)
    message = fields.Text(string="Message", required=True)

    def action_send(self):
        config = self.env['whatsapp.config'].search([], limit=1)
        if not config:
            raise UserError("WhatsApp config not found.")

        number = self.partner_id.mobile.replace('+', '').replace(' ', '')
        if not number:
            raise UserError("Customer mobile number is missing!")

        url = f"https://graph.facebook.com/v22.0/{config.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "text",
            "text": {
                "body": self.message
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if 'messages' in result:
            self.partner_id.message_post(
                body=f"✅ WhatsApp message sent:<br>{self.message}",
                message_type='comment'
            )
        else:
            raise UserError(f"WhatsApp Error: {result}")

        return {'type': 'ir.actions.act_window_close'}
