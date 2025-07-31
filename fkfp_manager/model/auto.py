from odoo import models, fields, api


class Auto(models.Model):
    _name = 'auto'
    _description = 'Auto Field'

    beneficiary_id = fields.Integer(string='Beneficiary ID', readonly=True, default=1)

    @api.model
    def create(self, vals):
        # Ensure the beneficiary_id starts from 1 and increments by 1
        if not vals.get('beneficiary_id'):
            max_beneficiary_id = self.search([], order='beneficiary_id desc', limit=1).beneficiary_id or 0
            vals['beneficiary_id'] = max_beneficiary_id + 1  # Increment the ID by 1

        return super(Auto, self).create(vals)
