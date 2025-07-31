from odoo import models, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class WhatsAppMetaService(models.AbstractModel):
    _name = 'whatsapp.meta.service'
    _description = 'Send WhatsApp Messages via Meta API'

    def send_director_notification(self, partner):
        config = self.env['whatsapp.config'].search([], limit=1)
        if not config:
            raise UserError("WhatsApp config not found.")

        # Hardcoded director number (must be in E.164 format without '+' or spaces)
        director_number = '923431221658'  # <-- Replace with actual number

        message = _(
            "📣 New Beneficiary Created\n"
            "Name: {name}\n"
            "Beneficiary ID: {beneficiary_id}"
        ).format(name=partner.name, beneficiary_id=partner.beneficiary_id or "N/A")

        url = f"https://graph.facebook.com/v22.0/{config.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": director_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if 'messages' in result:
            _logger.info("✅ WhatsApp message sent to director: %s", director_number)
        else:
            _logger.error("❌ WhatsApp Error: %s", result)
            raise UserError(f"WhatsApp Error: {result}")

    def send_director_notification_update(self, partner, action, changed_fields=None, old_value=None, new_value=None):
        config = self.env['whatsapp.config'].search([], limit=1)
        if not config:
            raise UserError("WhatsApp config not found.")

        director_number = '923431221658'

        if action == 'update':
            field_name = changed_fields[0] if changed_fields else 'a field'
            message = (
                f"✏️ Beneficiary Updated\n"
                f"Name: {partner.name}\n"
                f"Beneficiary ID: {partner.beneficiary_id or partner.id}\n"
                f"{field_name.capitalize()} changed:\n"
                f"{old_value} ➜ {new_value}"
            )
        else:
            return

        url = f"https://graph.facebook.com/v22.0/{config.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": director_number,
            "type": "text",
            "text": {"body": message}
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if 'messages' not in result:
            _logger.error("WhatsApp Error: %s", result)
            raise UserError(f"WhatsApp Error: {result}")
