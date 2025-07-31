from odoo import models, fields, api


class PhotoUploadWizard(models.TransientModel):
    _name = 'fkfp.photo.upload.wizard'
    _description = 'Photo Upload Wizard'

    image = fields.Binary(string='Photo', required=True)
    description = fields.Char(string='Description')

    def action_save_photo(self):
        active_partner_id = self.env.context.get('default_partner_id')
        category = self.env.context.get('default_category')

        self.env['fkfp.photo.gallery'].create({
            'partner_id': active_partner_id,
            'category': category,
            'image': self.image,
            'description': self.description,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fkfp.photo.gallery',
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('partner_id', '=', active_partner_id)],
            'context': {
                'default_partner_id': active_partner_id,
            }
        }
