from odoo import models, fields, api


class DocumentUploadWizard(models.TransientModel):
    _name = 'fkfp.document.upload.wizard'
    _description = 'Document Upload Wizard'

    file = fields.Binary(string='Document File', required=True)
    description = fields.Char(string='Description')

    def action_save_document(self):
        partner_id = self.env.context.get('default_partner_id')
        doc_type = self.env.context.get('default_document_type')

        self.env['fkfp.partner.document'].create({
            'partner_id': partner_id,
            'document_type': doc_type,
            'file': self.file,
            'description': self.description,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fkfp.partner.document',
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('partner_id', '=', partner_id)],
            'context': {'default_partner_id': partner_id}
        }
