from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime
import logging

_logger = logging.getLogger(__name__)


class InheritAccountMove(models.Model):
    _inherit = "account.move"

    partner_id = fields.Many2one('res.partner', string='Student', domain=[('is_student', '=', True)])
    x_studio_class = fields.Char(string='Class', readonly=True, store=True, related='partner_id.current_grade')
    x_studio_grade = fields.Char(string="Grade", store=True,
                                 readonly=True)
    x_studio_section = fields.Selection(related="partner_id.new_homeroom", string="Section", store=True, readonly=True)
    x_studio_enrollment_state = fields.Many2one(string="Enrollment state", readonly=True, store=True,
                                                related='partner_id.current_enroll_status')
    x_studio_date_field_pqveP = fields.Date(string='New Date', store=True, copy=True)
    x_studio_facts_id = fields.Integer(related="partner_id.facts_id", string="Facts ID", store=True, readonly=True)
    x_studio_inv = fields.Char(string='New Text', store=True, copy=True)
    x_studio_outstanding = fields.Float(string='outstanding', store=True, copy=True)
    x_studio_over_due_2 = fields.Boolean(string='over due 2', store=True, copy=True)
    student_code = fields.Char(string='Student Code', store=True, copy=True, related='partner_id.student_code')
    fee_months = fields.Many2many('x_billing_months', string='Fee Months')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ], default='draft')
    actual_fee = fields.Float(string='Actual Fee', store=True)
    concession_percent = fields.Integer(string='Concession', store=True)

    imported_payment_date = fields.Date(string="Imported Payment Date")

    @api.constrains('fee_months')
    def _onchange_fee_months(self):
        for line in self.invoice_line_ids:
            if line.product_id:
                month_names = ', '.join(self.fee_months.mapped('x_name'))
                line.name = f"{line.product_id.name} for {month_names}" if month_names else line.product_id.name

    @api.onchange('partner_id')
    def _onchange_current_grade(self):
        for record in self:
            record.x_studio_grade = record.partner_id.current_grade_selection

    @api.model
    def create(self, vals):
        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            vals['x_studio_grade'] = partner.current_grade_selection
        return super(InheritAccountMove, self).create(vals)

    def write(self, vals):
        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            vals['x_studio_grade'] = partner.current_grade_selection
        return super(InheritAccountMove, self).write(vals)

    def action_save_and_confirm(self):
        for record in self:
            # Save the record explicitly (ensure it's saved first)
            record.flush()  # This makes sure that all changes are committed to the database

            # Now update the state to 'posted'
            record.write({
                'state': 'posted',  # Change the state to 'posted'
            })

    @api.model
    def action_register_payments_scheduler(self):
        # Get today's date
        today = fields.Date.today()
        # Loop through each branch
        branches = self.env['res.branch'].search([])
        for branch in branches:
            # Fetch up to 500 open invoices with `imported_payment_date` set for this branch
            invoices = self.search([
                ('branch_id', '=', branch.id),
                ('state', '=', 'posted'),
                ('ol_payment_date_compute', '=', False),
                ('imported_payment_date', '!=', False),
                ('imported_payment_date', '<=', today),
                ('payment_state', '=', 'not_paid'),
                ('imported_payment_date', '<=', today)
            ], limit=500)
            payment_obj = self.env['account.payment']
            for invoice in invoices:
                # Create a payment for the invoice
                payment_vals = {
                    'partner_id': invoice.partner_id.id,
                    'amount': invoice.amount_residual,
                    'date': invoice.imported_payment_date,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
                    'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                }
                payment = payment_obj.create(payment_vals)
                payment.action_post()  # Post the payment
                # Reconcile the payment with the invoice
                receivable_lines = payment.line_ids.filtered(lambda l: l.account_internal_type == 'receivable')
                invoice_lines = invoice.line_ids.filtered(lambda l: l.account_internal_type == 'receivable')

                (receivable_lines + invoice_lines).reconcile()

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('move_id.fee_months')
    def _onchange_fee_months(self):
        if self.product_id and self.move_id.fee_months:
            month_names = ', '.join(self.move_id.fee_months.mapped('name'))
            self.name = f"{self.product_id.name} for {month_names}"
        else:
            self.name = self.product_id.name
