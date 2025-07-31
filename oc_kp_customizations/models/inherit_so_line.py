from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_sku = fields.Char(string="Product SKU")
    part_number = fields.Char(string="Part Number")

    @api.depends('product_id', 'product_id.name', 'product_id.product_template_attribute_value_ids')
    def _compute_name(self):
        for line in self:
            if line.product_id:
                # Get product name
                product_name = line.product_id.name
                variant_names = ", ".join(
                    line.product_id.product_template_attribute_value_ids.mapped('name')
                )
                line.name = f"{product_name} ({variant_names})" if variant_names else product_name
            else:
                line.name = ''

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_sku = self.product_id.default_code
            # Get product name
            product_name = self.product_id.name
            variant_names = ", ".join(
                self.product_id.product_template_attribute_value_ids.mapped('name')
            )
            self.name = f"{product_name} ({variant_names})" if variant_names else product_name

    def create(self, vals):
        if isinstance(vals, list):
            for val in vals:
                if 'product_id' in val and val['product_id']:
                    product = self.env['product.product'].browse(int(val['product_id']))
                    val['product_sku'] = product.default_code
                    variant_names = ", ".join(product.product_template_attribute_value_ids.mapped('name'))
                    val['name'] = f"{product.name} ({variant_names})" if variant_names else product.name

        else:
            if 'product_id' in vals and vals['product_id']:
                product = self.env['product.product'].browse(int(vals['product_id']))
                vals['product_sku'] = product.default_code

                # Get product name with variants
                variant_names = ", ".join(product.product_template_attribute_value_ids.mapped('name'))
                vals['name'] = f"{product.name} ({variant_names})" if variant_names else product.name

        return super(SaleOrderLine, self).create(vals)

    def write(self, vals):
        if 'product_id' in vals and vals['product_id']:
            product = self.env['product.product'].browse(int(vals['product_id']))
            vals['product_sku'] = product.default_code
            # Get product name with variants
            variant_names = ", ".join(product.product_template_attribute_value_ids.mapped('name'))
            vals['name'] = f"{product.name} ({variant_names})" if variant_names else product.name
        res = super(SaleOrderLine, self).write(vals)
        if 'part_number' in vals or 'product_sku' in vals:
            for line in self:
                update_vals = {}
                if 'part_number' in vals:
                    update_vals['part_number'] = vals['part_number']
                if 'product_sku' in vals:
                    update_vals['product_sku'] = vals['product_sku']
                stock_moves = self.env['stock.move'].search([('sale_line_id', '=', line.id)])
                for move in stock_moves:
                    move.write(update_vals)

        # for invoice in invoice_lines:
        #     invoice.write(update_vals)
        #     for invoice_line in invoice.invoice_line_ids:
        #         if invoice_line.sale_line_id.id == line.id:
        #             invoice_line.write(update_vals)
        return res
