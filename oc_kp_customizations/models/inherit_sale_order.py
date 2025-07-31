from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    po_number = fields.Char(string='PO number', store=True)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.picking_ids:
                for picking in order.picking_ids:
                    for move_line in picking.move_ids_without_package:
                        move_line.product_sku = move_line.product_id.default_code
                        matching_order_lines = order.order_line.filtered(lambda l: l.product_id == move_line.product_id)
                        move_line.part_number = matching_order_lines[:1].part_number if matching_order_lines else False
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
        for order in self:
            for line in order.order_line:
                invoice_line = invoices.invoice_line_ids.filtered(lambda l: l.sale_line_ids == line)
                invoice_line.update({
                    'product_sku': line.product_sku,
                    'part_number': line.part_number,
                })

        return invoices
