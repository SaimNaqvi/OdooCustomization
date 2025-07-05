from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class BillingMonth(models.Model):
    _inherit = 'account.move'

    # Making field to display billing month of subscription
    billingMonth = fields.Char(string='Billing Month', compute='_compute_billingMonth', index=True)
    billingMonth__ = fields.Char(string='Billing Month')
    

    # Computing billingMonth by using Next Invoice Date - Extracting the month and year from next
    # invoice date
    @api.depends('invoice_date')
    def _compute_billingMonth(self):
        for subscription in self:
            if subscription.invoice_date:
                if subscription.journal_id.name == 'Quarterly':
                    month_year = subscription.invoice_date.strftime('%b-%y')
                    adjusted_date = subscription.invoice_date + relativedelta(months=2)
                    month_year = month_year +' - '+ adjusted_date.strftime('%b-%y')
                elif subscription.journal_id.name == 'Bi Monthly':
                    month_year = subscription.invoice_date.strftime('%b-%y')
                    adjusted_date = subscription.invoice_date + relativedelta(months=1)
                    month_year = month_year +' - '+ adjusted_date.strftime('%b-%y')
                elif subscription.journal_id.name == 'Quadruple':
                    month_year = subscription.invoice_date.strftime('%b-%y')
                    adjusted_date = subscription.invoice_date + relativedelta(months=3)
                    month_year = month_year +' - '+ adjusted_date.strftime('%b-%y')
                
                else:
                    month_year = subscription.invoice_date.strftime('%b-%y')
                subscription.billingMonth = month_year
                subscription.billingMonth__ = month_year
                
            else:
                subscription.billingMonth = False
                subscription.billingMonth__ = False

# Creating wizard to update the next invoice date in subscriptions (in bulk)
# class UpdateRecurringNextDateWizard(models.TransientModel):
#     _name = 'update.recurring.next.date.wizard'
#     _description = 'Update Recurring Next Date Wizard'
    
#     # Field to update the next invoice date in subscription(s)
#     invoice_date = fields.Date(string='Bill Date')
    
#     # Function that will be trigerred once the confim button is hit
#     def update_records(self):
#         # Getting only those records that are selected
#         selected_records = self.env.context.get('active_ids')
#         if selected_records:
#             record_objs = self.env['account.move'].browse(selected_records)
#             # Updating the the next invoice date of these records based on the date selected through wizard
#             record_objs.write({'invoice_date': self.invoice_date})
        
#         return {'type': 'ir.actions.act_window_close'}