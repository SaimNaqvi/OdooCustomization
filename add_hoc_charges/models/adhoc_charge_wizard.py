from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AdhocChargeWizard(models.TransientModel):
    _name = 'adhoc.charge.wizard'
    _description = 'Ad Hoc Charge Wizard'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    unit_price = fields.Float(string='Unit Price', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)

    def add_charges(self):
        """Add the selected product as a line item to selected invoices."""
        context = self.env.context
        active_ids = context.get('active_ids', [])

        if not active_ids:
            raise UserError(_("No invoices selected."))

        invoices = self.env['account.move'].browse(active_ids)
        for invoice in invoices:
            if invoice.move_type != 'out_invoice' or invoice.state != 'draft':
                raise UserError(
                    _("Invoice %s is either not a customer invoice or is not in draft state.") % invoice.name)

            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                'quantity': self.quantity,
                'price_unit': self.unit_price,
                'account_id': self.product_id.property_account_income_id.id or self.product_id.categ_id.property_account_income_categ_id.id,
            })

