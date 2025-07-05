from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime


class InheritAccountJornal(models.Model):
    _inherit = "account.journal"

    allow_portal_registration = fields.Boolean(string="Allow Portal Registration")
    branch_id = fields.Many2one('res.branch', string='Branch', store=True)

    @api.model
    def default_get(self, default_fields):
        res = super(InheritAccountJornal, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id': self.env.user.branch_id.id or False
            })
        return res
