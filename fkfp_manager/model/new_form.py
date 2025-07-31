from odoo import models, fields, api


# Inherit the 'res.partner' model to add custom functionality
class ResPartner(models.Model):
    _inherit = 'res.partner'

    cost_ids = fields.One2many('fkfp_manager.cost', 'partner_id', string='Costs')
    donor_ids = fields.One2many('fkfp_manager.donor', 'partner_id', string='Donors')
    # photo_gallery_ids = fields.One2many('photo.gallery.line', 'partner_id', string='Photo Gallery')


# Custom model for Cost
class Cost(models.Model):
    _name = 'fkfp_manager.cost'
    _description = 'Cost'

    name = fields.Char(string="Name")
    amount = fields.Float(string="Amount")
    partner_id = fields.Many2one('res.partner', string='Partner')


# Custom model for Donor
class Donor(models.Model):
    _name = 'fkfp_manager.donor'
    _description = 'Donor'

    name = fields.Char(string="Name")
    contact_info = fields.Char(string="Contact Information")
    partner_id = fields.Many2one('res.partner', string='Partner')
