from odoo import api, fields, models
from odoo.exceptions import UserError


class BillingMonth(models.Model):
    _inherit = 'sale.subscription'

    # Making field to display billing month of subscription
    billing_month = fields.Char(string='Billing Month', compute='_compute_billing_month', store=True, index=True)

    # Computing billing_month by using Next Invoice Date - Extracting the month and year from next
    # invoice date
    @api.depends('recurring_next_date')
    def _compute_billing_month(self):
        for subscription in self:
            if subscription.recurring_next_date:
                month_year = subscription.recurring_next_date.strftime('%b-%y')
                subscription.billing_month = month_year
            else:
                subscription.billing_month = False


# Creating wizard to update the next invoice date in subscriptions (in bulk)
class UpdateRecurringNextDateWizard(models.TransientModel):
    _name = 'update.recurring.next.date.wizard'
    _description = 'Update Recurring Next Date Wizard'

    # Field to update the next invoice date in subscription(s)
    recurring_invoice_date = fields.Date(string='Next Invoice Date')

    # Function that will be trigerred once the confim button is hit
    def update_records(self):
        # Getting only those records that are selected
        selected_records = self.env.context.get('active_ids')
        if selected_records:
            record_objs = self.env['sale.subscription'].browse(selected_records)
            # Updating the the next invoice date of these records based on the date selected through wizard
            record_objs.write({'recurring_next_date': self.recurring_invoice_date})

        return {'type': 'ir.actions.act_window_close'}
