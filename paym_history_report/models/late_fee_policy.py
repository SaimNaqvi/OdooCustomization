from odoo import models, fields, api
from datetime import datetime, timedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _apply_late_fee(self):
        late_fee_product = self.env['product.product'].search([('name', '=', 'Late Fee')], limit=1)
        if not late_fee_product:
            return

        today = fields.Date.context_today(self)
        invoices = self.search([
            ('payment_state', 'in', ['partial', 'not_paid']),
            ('state', '=', 'posted'),
            ('invoice_date_due', '<', today),
        ])

        for invoice in invoices:
            if any(line.product_id == late_fee_product for line in invoice.invoice_line_ids):
                continue

            overdue_days = (today - invoice.invoice_date_due).days
            if overdue_days > 0:
                late_fee_line = {
                    'product_id': late_fee_product.id,
                    'quantity': 1,
                    'price_unit': late_fee_product.list_price,
                }
                invoice.write({'invoice_line_ids': [(0, 0, late_fee_line)]})
