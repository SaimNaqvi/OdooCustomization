from odoo import api, fields, models
from datetime import date
from odoo.exceptions import UserError
import math
from odoo.exceptions import ValidationError
import json


class account_move(models.Model):
    _inherit = 'account.move'

    total_arears = fields.Float(string='Total Arears', compute="_compute_arears")
    total_including_arears = fields.Float(string='Total Including Arears', compute="_compute_incl_arears")

    @api.depends('unpaid_std_ids.amount_total_signed')
    def _compute_arears(self):
        for record in self:
            total = sum(record.unpaid_std_ids.mapped('amount_residual_signed'))
            record.total_arears = total

    @api.depends('total_arears', 'tax_totals_json')
    def _compute_incl_arears(self):
        for record in self:
            # json_dict = json.loads(record.tax_totals_json)
            record.total_including_arears = record.total_arears + record.amount_residual


class account_payment_register(models.TransientModel):
    _inherit = 'account.payment.register'

    include_arears = fields.Boolean(string='Include Arears', default=False)
    total_arears = fields.Float(string='Total Arears', default=0)
    total_including_arears = fields.Float(string='Total Including Arears', default=0)

    @api.onchange('include_arears')
    def _update_arears(self):

        for rec in self:
            if rec.include_arears:
                try:
                    invoice = self.env['account.move'].search([
                        ('name', '=', self.communication),
                    ])

                    rec.total_arears = invoice.total_arears
                    rec.total_including_arears = invoice.total_including_arears
                except:
                    raise UserError("Invoice doesn't exists as provided in Memo field.")


            else:
                rec.total_arears = 0
                rec.total_including_arears = 0

    @api.onchange('total_including_arears')
    def amount_including_arears(self):
        for record in self:
            if record.include_arears == True:
                record.amount = record.total_including_arears
            else:
                active_record = self.env['account.move'].browse(self._context['active_id'])
                if record.late_fee_amt:
                    record.amount = active_record.amount_residual + record.late_fee_amt
                else:
                    record.amount = active_record.amount_residual
