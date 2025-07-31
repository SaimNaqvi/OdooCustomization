import base64
import io
import zipfile
from odoo import models, fields, api


class PhotoGallery(models.Model):
    _name = 'fkfp.photo.gallery'
    _description = 'Photo Gallery for Beneficiaries'
    _order = 'date desc'

    partner_id = fields.Many2one('res.partner', string='Beneficiary', required=True, ondelete='cascade')
    image = fields.Binary(string='Photo', attachment=True, required=True)
    category = fields.Selection([
        ('before', 'Before'),
        ('follow_up', 'Follow Up'),
        ('after', 'After')
    ], string='Photo Type', required=True)
    description = fields.Char(string='Description')
    date = fields.Date(string='Date', default=fields.Date.context_today)

    @api.model
    def download_selected_photos(self, record_ids):
        records = self.browse(record_ids)
        zip_buffer = io.BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, 'w')

        for rec in records:
            if rec.image:
                image_data = base64.b64decode(rec.image)
                file_name = f"{rec.partner_id.name or 'unknown'}_{rec.category}_{rec.id}.jpg"
                zip_file.writestr(file_name, image_data)

        zip_file.close()
        zip_content = base64.b64encode(zip_buffer.getvalue())

        attachment = self.env['ir.attachment'].create({
            'name': 'photos.zip',
            'type': 'binary',
            'datas': zip_content,
            'mimetype': 'application/zip',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
