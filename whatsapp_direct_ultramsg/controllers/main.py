from odoo import http
from odoo.http import request
import base64


class WhatsAppPublicAttachment(http.Controller):

    @http.route('/whatsapp/public_file/<int:attachment_id>', type='http', auth='none', website=True)
    def download_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        print("\n\n\n\natt",attachment)
        if not attachment.exists():
            return request.not_found()
        file_data = base64.b64decode(attachment.datas)
        # headers = [
        #     ('Content-Type', attachment.mimetype or 'application/octet-stream'),
        #     ('Content-Disposition', f'inline; filename="{attachment.name}"'),
        # ]
        headers = [
            ('Content-Type', attachment.mimetype or 'application/octet-stream'),
            ('Content-Disposition', f'inline; filename="{attachment.name}"'),
            ('Content-Length', str(len(file_data))),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ]
        return request.make_response(file_data, headers=headers)
