from odoo import api, fields, models, _


class StudentConcession(models.Model):
    _name = 'user.define.data'
    _description = 'User Define data'

    id = fields.Integer(string='Id')
    data_id = fields.Integer(string='Data Id')
    field_id = fields.Integer(string='Field Id')
    linked_id = fields.Integer(string='Linked Id')
    data = fields.Text(string='Data')
