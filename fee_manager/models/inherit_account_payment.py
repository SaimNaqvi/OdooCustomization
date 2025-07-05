from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime
import calendar


class InheritAccountPayment(models.Model):
    _inherit = "account.payment"

    student_bill = fields.Char(string='Student Bill Number', index=True, tracking=True)
    month = fields.Char(string='Month')
    payment_status = fields.Char(string='payment_status', store=True)

    registration_number = fields.Char('Registration Number')
    student_code = fields.Char('Student ID')
    amount_billed = fields.Float(string='Amount Billed', store=True, readonly=True)
    due_date = fields.Date(string="Due Date", compute='_compute_due_date', store=True)

    # Keep invoice_id as internal reference only (not meant for user input)
    invoice_id = fields.Many2one('account.move', string='Linked Invoice', readonly=True)

    @api.model
    def get_bill_details(self, bill_number):
        bill = self.env['account.move'].sudo().search([('bill_number', '=', bill_number), ('state', '=', 'posted')], limit=1)
        if bill:
            return {
                'partner_id': bill.partner_id.id,
                'amount': bill.amount_total,
                'reference': bill.name
            }
        else:
            return {}

    @api.depends('student_bill')
    def _compute_due_date(self):
        for payment in self:
            if payment.student_bill and payment.invoice_id:
                payment.due_date = payment.invoice_id.invoice_date_due
            else:
                payment.due_date = False

    @api.model
    def create(self, vals):
        # Find the invoice based on the provided student_bill
        if 'student_bill' in vals:
            vals['invoice_id'] = self._find_invoice(vals)
        # Map the amount if provided
        if 'amount_received' in vals:
            vals['amount_received'] = float(vals.get('amount_received', 0.0))
        # Create the payment record
        record = super(InheritAccountPayment, self).create(vals)
        # Trigger onchange if needed
        if 'student_bill' in vals or 'student_code' in vals or 'registration_number' in vals:
            record._onchange_student_data()
        return record

    def write(self, vals):
        if 'student_bill' in vals:
            invoice = self._find_invoice_by_bill_number(vals['student_bill'])
            if invoice:
                vals['invoice_id'] = invoice.id
        # Map the amount if provided
        if 'amount_received' in vals:
            vals['amount_received'] = float(vals.get('amount_received', 0.0))
        elif 'student_code' in vals:
            student = self.env['res.partner'].sudo().search(
                [('student_code', '=', vals['student_code'])], limit=1)
            if student:
                vals['partner_id'] = student.id
        res = super(InheritAccountPayment, self).write(vals)
        if 'student_bill' in vals and self.invoice_id:
            self._onchange_student_data()
        return res

    def _find_invoice_by_bill_number(self, bill_number):
        """Helper to find invoice by bill number"""
        return self.env['account.move'].sudo().search([
            ('name', '=', bill_number),
            ('state', '=', 'posted')
        ], limit=1)

    def _find_invoice(self, vals):
        """
        Find invoice based on available information in this order:
        1. student_bill (bill number)
        2. student_code
        3. registration_number
        """
        AccountMove = self.env['account.move']
        ResPartner = self.env['res.partner']
        invoice = None

        # Case 1: Search by Student Bill Number
        bill_number = vals.get('student_bill')
        if bill_number:
            invoice = self._find_invoice_by_bill_number(bill_number)

        # Case 2: Search by Student Code
        if not invoice:
            student_code = vals.get('student_code')
            if student_code:
                student = ResPartner.sudo().search(
                    [('student_code', '=', student_code)], limit=1)
                if student:
                    invoice = AccountMove.sudo().search([
                        ('partner_id', '=', student.id),
                        ('state', '=', 'posted')
                    ], order='date desc', limit=1)

        # Case 3: Search by Registration Number
        if not invoice:
            reg_number = vals.get('registration_number')
            if reg_number:
                student = ResPartner.sudo().search(
                    [('reg_number', '=', reg_number)], limit=1)
                if student:
                    invoice = AccountMove.sudo().search([
                        ('partner_id', '=', student.id),
                        ('state', '=', 'posted')
                    ], order='date desc', limit=1)

        return invoice.id if invoice else False

    @api.onchange('student_bill', 'student_code', 'registration_number')
    def _onchange_student_data(self):
        AccountMove = self.env['account.move']
        ResPartner = self.env['res.partner']

        if self.student_bill:
            invoice = self._find_invoice_by_bill_number(self.student_bill)
            if invoice:
                self.invoice_id = invoice.id
                self.partner_id = invoice.partner_id
                self.branch_id = invoice.branch_id
                self.ref = invoice.name
                self.registration_number = invoice.partner_id.reg_number
                self.student_code = invoice.partner_id.student_code
                self.amount_billed = sum(invoice.invoice_line_ids.mapped('price_subtotal'))
                due_date = self.sudo().invoice_id.invoice_date_due
                self.month = calendar.month_name[due_date.month] if due_date else False
                if self.invoice_id.payment_state == 'paid':
                    self.payment_status = 'Paid'
                else:
                    self.payment_status = 'Not Paid'

            else:
                return {
                    'warning': {
                        'title': "Bill Not Found",
                        'message': f"No posted invoice found with number {self.student_bill}"
                    }
                }
        elif self.student_code:
            student = ResPartner.sudo().search(
                [('student_code', '=', self.student_code)], limit=1)
            if student:
                self.registration_number = student.reg_number
                self.partner_id = student.id
                self.branch_id = student.branch_id
                invoice = AccountMove.sudo().search([
                    ('partner_id', '=', student.id),
                    ('state', '=', 'posted')
                ], order='date desc', limit=1)
                if invoice:
                    self.invoice_id = invoice.id
                    self.student_bill = invoice.name
                    due_date = self.sudo().invoice_id.invoice_date_due
                    self.month = calendar.month_name[due_date.month] if due_date else False
                    if self.invoice_id.payment_state == 'paid':
                        self.payment_status = 'Paid'
                    else:
                        self.payment_status = 'Not Paid'

        elif self.registration_number:
            student = ResPartner.sudo().search(
                [('reg_number', '=', self.registration_number)], limit=1)
            if student:
                self.student_code = student.student_code
                self.partner_id = student.id
                self.branch_id = student.branch_id
                invoice = AccountMove.sudo().search([
                    ('partner_id', '=', student.id),
                    ('state', '=', 'posted')
                ], order='date desc', limit=1)
                if invoice:
                    self.invoice_id = invoice.id
                    self.student_bill = invoice.name
                    due_date = self.sudo().invoice_id.invoice_date_due
                    self.month = calendar.month_name[due_date.month] if due_date else False
                    if self.invoice_id.payment_state == 'paid':
                        self.payment_status = 'Paid'
                    else:
                        self.payment_status = 'Not Paid'

    def action_post(self):
        for payment in self:
            if payment.state == 'draft':
                super(InheritAccountPayment, payment).action_post()
                payment._reconcile_payment_with_invoice()

    def _reconcile_payment_with_invoice(self):
        for payment in self:
            if payment.invoice_id and payment.state == 'posted':
                invoice_lines = payment.invoice_id.line_ids.filtered(
                    lambda line: line.account_id.internal_type == 'receivable' and not line.reconciled)
                payment_lines = payment.move_id.line_ids.filtered(
                    lambda line: line.account_id.internal_type == 'receivable' and not line.reconciled)

                # Reconcile the payment lines with the invoice lines
                (invoice_lines + payment_lines).reconcile()

                # Optionally update the payments widget on the invoice
                payment.invoice_id._compute_payments_widget_to_reconcile_info()
