from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_sku = fields.Char(string='Product SKU')
    part_number = fields.Char(string='Part Number')

    @api.depends('product_id', 'product_id.name')
    def _compute_name(self):
        for line in self:
            # Only use the product's name for the description
            if line.product_id:
                line.name = line.product_id.name
            else:
                line.name = ''

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_sku = self.product_id.default_code
            self.name = self.product_id.name

    @api.model
    def create(self, vals):
        if 'product_id' in vals and vals['product_id']:
            product = self.env['product.product'].browse(int(vals['product_id']))
            vals['product_sku'] = product.default_code
        # Ensure name is computed at creation
        if 'product_id' in vals:
            product = self.env['product.product'].browse(vals['product_id'])
            vals['name'] = product.name
        return super(PurchaseOrderLine, self).create(vals)

    def write(self, vals):
        if 'product_id' in vals and vals['product_id']:
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_sku'] = product.default_code

        res = super(PurchaseOrderLine, self).write(vals)

        if 'part_number' in vals or 'product_sku' in vals:
            for line in self:
                update_vals = {}
                if 'part_number' in vals:
                    update_vals['part_number'] = vals['part_number']
                if 'product_sku' in vals:
                    update_vals['product_sku'] = vals['product_sku']

                # Update corresponding stock move lines in GRN
                stock_moves = self.env['stock.move'].search([('purchase_line_id', '=', line.id)])
                for move in stock_moves:
                    move.write(update_vals)

                # Update corresponding vendor bill lines
                invoice_lines = self.env['account.move.line'].search([('purchase_line_id', '=', line.id)])
                for invoice_line in invoice_lines:
                    invoice_line.write(update_vals)

        return res
