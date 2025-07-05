from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from datetime import date


class AccountMove(models.Model):
    _inherit = 'account.move'

    total_pending_fee = fields.Float(compute='_compute_total_pending_fee', store=False)
    unpaid_months = fields.Integer(compute='_compute_total_pending_fee', store=False)

    registered_payments = fields.Many2many(
        'account.payment',
        'account_move_payment_rel',
        'account_move_id',
        'payment_id',
        string='Registered Payments',
        help='The payments registered for this invoice',
        domain="[('state','=','posted'),('partner_id','=',partner_id)]",
        compute='_compute_registered_payments',
        readonly=True,
        limit=4,
    )

    payment_history_ids = fields.One2many('payment.history', 'account_move_id', string='Payment History', store=True,
                                          index=True)

    @api.depends('partner_id')
    def _compute_total_pending_fee(self):
        for record in self:
            total_pending_fee = 0
            unpaid_months = 0
            if record.partner_id:
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('state', '=', 'posted'),
                    ('amount_residual', '>', 0)
                ])
                unpaid_months = len(invoices)
                total_pending_fee = sum(invoice.amount_residual for invoice in invoices)
            record.total_pending_fee = total_pending_fee
            record.unpaid_months = unpaid_months

    def action_register_payment(self):
        # Fetch the student (partner_id) from the created invoice
        student_id = self.partner_id
        if student_id:
            # Get the current date and calculate the date 12 months ago
            end_date = self.invoice_date
            start_date = end_date - timedelta(days=335)
            # Fetch invoices for the same student in the last 12 months
            past_invoices = self.env['account.move'].search([
                ('partner_id', '=', student_id.id),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('state', '=', 'posted')  # Assuming you want only posted invoices
            ])
            # Group invoices by month
            monthly_invoices = {}
            for past_invoice in past_invoices:
                month = past_invoice.invoice_date.strftime('%B %Y')
                if month not in monthly_invoices:
                    monthly_invoices[month] = {
                        'account_move_id': self.id,
                        'partner_id': student_id.id,
                        'month': month,
                        'invoice_date': past_invoice.invoice_date,
                        'payment_date': past_invoice.ol_payment_date_compute,
                        # Replace with actual payment date field if different
                        'amount': past_invoice.amount_total,
                    }
                else:
                    monthly_invoices[month]['amount'] += past_invoice.amount_total

            # Create payment history records
            for record in monthly_invoices.values():
                self.env['payment.history'].create(record)


        invoice = super(AccountMove, self).action_register_payment()
        return invoice

    def _compute_registered_payments(self):
        for move in self:
            move.registered_payments = False
            payments = self.env['account.payment'].search([
                ('state', '=', 'posted'),
                ('partner_id', '=', move.partner_id.id),
                # ('invoice_ids', 'in', [move.id]),
            ])
            move.registered_payments = [(6, 0, payments.ids)]

        for record in self:
            if record.partner_id:
                student_id = record.partner_id.id
                current_date = self.invoice_date if self.invoice_date else self.date
                start_date = (current_date - relativedelta(months=11)).replace(day=1)

                # Fetch the past 12 months' invoices for the same student
                past_invoices = self.env['account.move'].search([
                    ('partner_id', '=', student_id),
                    ('state', '=', 'posted'),  # Assuming you only want posted invoices
                    ('invoice_date', '>=', start_date), ('invoice_date', '<=', self.invoice_date)
                ])

                # Dictionary to hold aggregated data per month
                payment_history_data = {}

                for invoice in past_invoices:
                    month_year = invoice.invoice_date.strftime('%B %Y')
                    if month_year not in payment_history_data:
                        payment_history_data[month_year] = {
                            'account_move_id': record.id,
                            'partner_id': student_id,
                            'month': month_year,
                            'invoice_date': invoice.invoice_date,
                            'payment_date': invoice.ol_payment_date_compute,
                            # Adjust this if you have a different payment date field
                            'amount': invoice.amount_total,
                        }
                    else:
                        payment_history_data[month_year]['amount'] += invoice.amount_total

                # Create or update the payment history records
                record.payment_history_ids = [(5, 0, 0)]  # Clear existing records
                record.payment_history_ids = [(0, 0, data) for data in payment_history_data.values()]
            else:
                record.payment_history_ids = [(5, 0, 0)]  #

    def get_payment_history_by_month(self):
        self.ensure_one()
        current_date = self.invoice_date_due or fields.Date.today()
        start_date = current_date - relativedelta(months=12)

        # Fetch past 12 months invoices for this student
        invoices = self.env['account.move'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date_due', '>=', start_date),
            ('invoice_date_due', '<=', current_date),
        ])

        # Organize data by month name (e.g., 'January', 'February', ...)
        month_data = {}
        for inv in invoices:
            month = inv.invoice_date.strftime('%B')  # Full month name
            year = inv.invoice_date.strftime('%Y')
            payment = inv._get_first_payment()

            month_data[month] = {
                'amount': inv.amount_total,
                'paid_date': inv.ol_payment_date_compute,
                'year': year,
            }
        return month_data

    def _get_first_payment(self):
        lines = self.line_ids.filtered(lambda l: l.account_id.internal_type == 'receivable' and l.payment_id)
        for line in lines:
            return line.payment_id
        return None


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    month_year = fields.Char(string="Month/Year", compute="_compute_month_year", store=True)
    payment_date_custom = fields.Char(string="Payment Date", compute="_compute_payment_date_ddmmyyyy", store=True)

    @api.depends('date')
    def _compute_payment_date_ddmmyyyy(self):
        for record in self:
            if record.date:
                pay_date = str(record.date)
                payment_date_custom = '-'.join(pay_date.split('-')[::-1])
                record.payment_date_custom = payment_date_custom

    @api.depends('date')
    def _compute_month_year(self):
        for record in self:
            if record.date:
                month_year = record.date.strftime("%m-%Y")
                record.month_year = month_year


class PaymentHistory(models.Model):
    _name = 'payment.history'
    _description = 'Payment History'

    account_move_id = fields.Many2one('account.move', string='Invoice', help="Link to the invoice")
    partner_id = fields.Many2one('res.partner', string='Student', domain=[('is_student', '=', True)])
    month = fields.Char(string='Month', store=True, index=True)
    invoice_date = fields.Date(string='Invoice Date', store=True, index=True)
    payment_date = fields.Date(string='Payment Date', store=True, index=True)
    amount = fields.Float(string='Amount', store=True, index=True)
