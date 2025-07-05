import requests
import logging
from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WhatsAppSendWizard(models.TransientModel):
    _name = 'whatsapp.send.wizard'
    _description = 'Send WhatsApp Message Wizard'

    partner_id = fields.Many2one('res.partner', string="Recipient", required=True)
    message = fields.Text(string="Message", required=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")

    def action_send(self):
        config = self.env['whatsapp.config'].search([], limit=1)
        if not config:
            raise UserError("WhatsApp API not configured!")

        number = self.partner_id.mobile
        if not number:
            raise UserError("Customer mobile number is missing!")

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not base_url:
            raise UserError("System parameter 'web.base.url' is not configured.")

        success_logs = []
        error_logs = []

        # STEP 1: Send the message
        try:
            msg_payload = {
                'token': config.token,
                'to': number,
                'body': self.message
            }
            msg_url = f"https://api.ultramsg.com/{config.instance_id}/messages/chat"
            # response = requests.post(msg_url, data=msg_payload)
            # _logger.info("Text message response: %s", response.text)
            # result = response.json()
            # if result.get("sent") == "true":
            #     success_logs.append("Text message sent.")
            # else:
            #     error_logs.append("Text message failed.")
        except Exception as e:
            error_logs.append(f"Message send error: {str(e)}")

        # STEP 2: Send attachments (image + document)
        for attachment in self.attachment_ids:
            mimetype = attachment.mimetype or ''
            filename = attachment.name or 'document'
            # attachment.public = True
            db_name = self.env.cr.dbname
            attachment.sudo().write({'public': True})

            file_url = f"{base_url}/whatsapp/public_file/{attachment.id}"
            _logger.info("Preparing file: %s", file_url)

            if 'image' in mimetype:
                try:
                    image_url = f"https://api.ultramsg.com/{config.instance_id}/messages/image"
                    image_payload = {
                        'token': config.token,
                        'to': number,
                        'caption': filename,
                        'url': file_url
                    }
                    print("\n\n\n\nurl",image_payload)
                    response = requests.post(image_url, data=image_payload)
                    _logger.info("Image response: %s", response.text)

                    if '"sent":true' in response.text:
                        success_logs.append(f"Image sent: {filename}")
                    else:
                        error_logs.append(f"Image failed: {filename}")
                except Exception as e:
                    error_logs.append(f"Image send error: {str(e)}")

            else:
                try:
                    # Use clean dict for x-www-form-urlencoded
                    doc_url = f"https://api.ultramsg.com/{config.instance_id}/messages/document"
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

                    params = {
                        'token': config.token,
                        'to': number,
                        'filename': filename,
                        'document': file_url,
                        'caption': filename
                    }

                    _logger.info("📦 Document Payload: %s", params)
                    _logger.info("🌐 Document URL: %s", doc_url)

                    response = requests.post(doc_url, data=params, headers=headers)
                    _logger.info("📩 Document Response: %s", response.text)
                    result = response.json()

                    if result.get("sent") == "true":
                        success_logs.append(f"Document sent: {filename}")
                    else:
                        error_logs.append(f"Document failed: {filename}")
                except Exception as e:
                    error_logs.append(f"Document send error: {str(e)}")

        # Final notification
        message = ""
        if success_logs:
            message += "✅ Sent:\n" + "\n".join(success_logs)
        if error_logs:
            message += "\n\n❌ Failed:\n" + "\n".join(error_logs)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'WhatsApp Message Result',
                'message': message,
                'type': 'success' if not error_logs else 'warning',
            }
        }
