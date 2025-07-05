from datetime import timedelta
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class BillingMonthsWizard(models.TransientModel):
    _name = 'billing.months.wizard'
    _description = 'Billing Months Wizard'

    # Many2many field to hold the selected billing months (hidden from user)
    line_months_subscription_line = fields.Many2many(
        'x_billing_months', string='Selected Billing Months', invisible=True
    )

    # Due Date field for the wizard (default will be 9 days after the invoice date)
    recurring_next_date = fields.Date(string="Due Date", default=fields.Date.today)

    @api.model
    def default_get(self, fields_list):
        res = super(BillingMonthsWizard, self).default_get(fields_list)

        # Fetch selected records via active_ids passed from the context
        active_ids = self.env.context.get('active_ids', [])

        # Browse the selected records from the 'sale.subscription' model using active_ids
        selected_records = self.env['sale.subscription'].browse(active_ids)

        # Set the default 'recurring_next_date' based on the first selected subscription's due date
        if selected_records:
            # Assuming that all selected subscriptions have the same recurring next date
            subscription_due_date = selected_records[0].recurring_next_date or fields.Date.today()

            # Set the default due date to 9 days after the recurring next date
            due_date = fields.Date.from_string(subscription_due_date) + timedelta(days=9)
            res['recurring_next_date'] = fields.Date.to_string(due_date)

        return res

    def create_bills(self):
        invoices = self.env['account.move']

        # Fetch selected records via active_ids passed from the context
        active_ids = self.env.context.get('active_ids', [])

        # Browse the selected records from the 'sale.subscription' model using active_ids
        selected_records = self.env['sale.subscription'].browse(active_ids)

        for rec in selected_records:
            # Invoice date will be the first day of the next month, based on the current recurring_next_date
            invoice_date = fields.Date.from_string(rec.recurring_next_date)
            fee_plan_invoice_date = fields.Date.from_string(rec.recurring_next_date) + relativedelta(months=1, day=1)

            # Check if the field exists and is accessible
            invoice_lines = []
            if hasattr(rec, 'recurring_invoice_line_ids'):
                next_month = invoice_date.strftime('%b')
                domain = [('product_id', '!=', False),
                          ('line_months_subscription_line.x_name', '=', next_month)]

                products = rec.mapped('recurring_invoice_line_ids').filtered_domain(domain).product_id

                # Generate invoice lines only if recurring_invoice_line_ids is not empty
                if rec.recurring_invoice_line_ids:
                    for prod in products:
                        for line in rec.recurring_invoice_line_ids:
                            if line.product_id.id == prod.id:
                                invoice_lines.append((0, 0, {
                                    'product_id': line.product_id.id,
                                    'name': line.name,
                                    'quantity': 1,
                                    'price_unit': line.price_unit,
                                }))
            else:
                raise UserError("The field 'recurring_invoice_line_ids' is not available on this subscription record.")

            # Handle cases where there are no invoice lines
            if not invoice_lines:
                raise UserError("No invoice lines found to generate the invoice.")

            # The due date is now the one selected by the user in the wizard
            invoice_date_due = self.recurring_next_date  # Use the due date set by the user

            # Prepare the invoice values
            invoice_vals = {
                'partner_id': rec.partner_id.id,
                'invoice_date': invoice_date,  # Use the calculated next month's 1st date for the invoice date
                'move_type': 'out_invoice',
                'journal_id': rec.x_studio_journal.id,
                'invoice_line_ids': invoice_lines,
                'invoice_ref': rec.id,
                'branch_id': rec.partner_id.branch_id.id,
                'invoice_date_due': invoice_date_due,  # Set the user-selected due date
            }

            # Create the invoice
            invoice = rec.env['account.move'].create(invoice_vals)

            # Update the recurring_next_date on the subscription record to the next month's 1st date
            rec.recurring_next_date = fee_plan_invoice_date  # Set the next billing date to the 1st of next month

            invoices += invoice

        return invoices
