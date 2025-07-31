from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    nature_donation = fields.Char(string="Nature of donation")
    amount_words = fields.Char(string="Amount in words")
    brief_description = fields.Char(string="Brief description of donation")
    received_with = fields.Char(string="Received with thanks from")
