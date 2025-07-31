from odoo import models, fields, api


class FkfpDonor(models.Model):
    _name = 'fkfp.donor'
    _description = 'Donor Information'

    _rec_name = 'donor_partner_id'

    donor_partner_id = fields.Many2one('res.partner', string='Donor', required=True, domain=[('title', '=', 'Donor')])
    donor_nationality = fields.Selection(string='Nationality', related='donor_partner_id.nationality', store=True)
    phone = fields.Char(string='Phone', related='donor_partner_id.phone', store=True)
    mobile = fields.Char(string='Mobile', related='donor_partner_id.mobile', store=True)
    email = fields.Char(string='Email', related='donor_partner_id.email', store=True)
    cnic = fields.Char(string='CNIC', related='donor_partner_id.cnic', store=True)
    address = fields.Char(string='Address', related='donor_partner_id.street', store=True)
    country_id = fields.Many2one('res.country', string='Country', related='donor_partner_id.country_id', store=True)

    donated_amount = fields.Float(string='Donated Amount', store=True)
    beneficiary_ids = fields.Many2many('res.partner', 'fkfp_donor_beneficiary_rel', 'donor_id', 'beneficiary_id',
                                       string='Beneficiaries')

    donor_line_ids = fields.One2many('fkfp.donor.line', 'donor_id', string='Beneficiaries')

