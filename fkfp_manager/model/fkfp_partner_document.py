from odoo import models, fields, api


class PartnerDocument(models.Model):
    _name = 'fkfp.partner.document'
    _description = 'Documents for Beneficiaries'
    _order = 'date desc'

    partner_id = fields.Many2one('res.partner', string='Beneficiary', required=True, ondelete='cascade')
    document_type = fields.Selection([
        ('nic_front', 'NIC Front'),
        ('nic_back', 'NIC Back'),
        ('stamp_paper', 'Stamp Paper'),
        ('das', 'DAS'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    file = fields.Binary(string='Document File', attachment=True, required=True)
    description = fields.Char(string='Description')
    date = fields.Date(string='Upload Date', default=fields.Date.context_today)
