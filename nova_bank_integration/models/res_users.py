from odoo import models, fields


class InheritResUsers(models.Model):
    _inherit = 'res.users'

    # api_login_time = fields.Datetime(string="API Login Time")
