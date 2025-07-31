import base64
import requests
import mimetypes
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class WhatsAppSendWizard(models.TransientModel):
    _name = 'fkfp.whatsapp.message.wizard'
    _description = 'WhatsApp Message Wizard'

    staff_id = fields.Many2one(
        'fkfp.staff', string='Staff', required=True,
        default=lambda self: self.env['fkfp.staff'].browse(self.env.context.get('active_id'))
    )
    message = fields.Text(string='Message')
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    filename = fields.Char(string='File Name')

    def action_send_whatsapp(self):
        config = self.env['whatsapp.config'].search([], limit=1)
        if not config:
            raise UserError("WhatsApp config not found.")

        partner = self.staff_id
        if not partner:
            raise UserError("No linked partner found for selected staff.")

        number = partner.mobile.replace('+', '').replace(' ', '')
        if not number:
            raise UserError("Customer mobile number is missing!")
        if number[0] == '0':
            number = number.replace('0', '92')
        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json"
        }

        # ✅ 1. Send text message first (if provided)
        if self.message:
            payload = {
                "messaging_product": "whatsapp",
                "to": number,
                "type": "text",
                "text": {"body": self.message}
            }
            text_response = requests.post(
                f"https://graph.facebook.com/v22.0/{config.phone_number_id}/messages",
                headers=headers,
                json=payload
            )
            text_result = text_response.json()
            if 'messages' not in text_result:
                raise UserError(f"Text message failed: {text_result}")

        # ✅ 2. Send each attachment
        for attachment in self.attachment_ids:
            file_data = base64.b64decode(attachment.datas)
            mime_type = attachment.mimetype or self._guess_mime_type(attachment.name)

            # 2.1 Upload to Meta's /media endpoint
            upload_url = f"https://graph.facebook.com/v22.0/{config.phone_number_id}/media"
            upload_headers = {"Authorization": f"Bearer {config.access_token}"}
            files = {
                'file': (attachment.name, file_data, mime_type),
                'messaging_product': (None, 'whatsapp')
            }

            upload_response = requests.post(upload_url, headers=upload_headers, files=files)
            upload_result = upload_response.json()

            if 'id' not in upload_result:
                raise UserError(f"File upload failed: {upload_result}")

            media_id = upload_result['id']

            # 2.2 Send the media as document
            send_url = f"https://graph.facebook.com/v22.0/{config.phone_number_id}/messages"
            send_payload = {
                "messaging_product": "whatsapp",
                "to": number,
                "type": "document",
                "document": {
                    "id": media_id,
                    "filename": attachment.name
                }
            }

            send_response = requests.post(send_url, headers=headers, json=send_payload)
            send_result = send_response.json()

            if 'messages' not in send_result:
                raise UserError(f"File send failed: {send_result}")

        return {'type': 'ir.actions.act_window_close'}

    def _guess_mime_type(self, filename):
        mime, _ = mimetypes.guess_type(filename)
        return mime or 'application/octet-stream'
