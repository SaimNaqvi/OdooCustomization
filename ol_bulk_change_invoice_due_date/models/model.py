
from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime

class bulk_edit_move_wiz(models.TransientModel):
    _name='account.bulk_edit_move_wiz'
    invoice_date_due = fields.Date('invoice_date_due')
    account_move_ids = fields.Many2many('account.move', string='account_moves')
    def apply(self):
        for wizard in self:
            for move in wizard.account_move_ids:
                move.invoice_date_due=wizard.invoice_date_due


    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)
        ids=self._context.get("active_ids")
        res["account_move_ids"]=[(6,0,ids)]
        return res

class invoice_ext(models.Model):

    _inherit = "account.move"
    def action_open_bulk_edit_move_wizard(self):

        return {
            'name': _('Bulk Edit Due Date'),
            'res_model': 'account.bulk_edit_move_wiz',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
