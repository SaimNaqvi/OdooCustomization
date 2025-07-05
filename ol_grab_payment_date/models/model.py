from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime

class ext_invoice(models.Model):
    _inherit = "account.move"
    
    ol_payment_date_compute = fields.Date(string='Payment Date', compute="_calculate_date_paid")
    ol_payment_date = fields.Date(string='Payment Date')

    @api.depends('invoice_payments_widget')
    def _calculate_date_paid(self):
        for rec in self:
            if rec.invoice_payments_widget:
                # Find the index of the 'date' field in the string
                date_index = rec.invoice_payments_widget.find('"date"')

                if date_index != -1:
                    # Find the starting index of the date value
                    date_start_index = rec.invoice_payments_widget.find('"', date_index + 7) + 1

                    # Find the ending index of the date value
                    date_end_index = rec.invoice_payments_widget.find('"', date_start_index)

                    # Extract the date value from the string
                    date_str = rec.invoice_payments_widget[date_start_index:date_end_index]

                    try:
                        # Try to parse the date with the expected format
                        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        # Handle the case when the date is not in the expected format
                        date = False
                else:
                    date = False

                # Update the computed field
                rec.ol_payment_date_compute = date
                rec.ol_payment_date = date
