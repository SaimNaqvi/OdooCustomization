from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_sku = fields.Char(string='Product SKU', related='purchase_line_id.product_sku', store=True)
    part_number = fields.Char(string='Part Number', related='purchase_line_id.part_number', store=True)
