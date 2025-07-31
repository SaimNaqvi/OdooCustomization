from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_sku = fields.Char(string='Product SKU', related='product_id.default_code', store=True)
    part_number = fields.Char(string='Part Number')


    @api.model
    def create(self, vals):
        if 'purchase_line_id' in vals:
            purchase_line = self.env['purchase.order.line'].browse(vals['purchase_line_id'])
            vals['part_number'] = purchase_line.part_number
        return super(StockMove, self).create(vals)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    number_of_boxes = fields.Integer(string="Number of Boxes", default=0)
    number_of_pallets = fields.Integer(string="Number of Boxes", default=0)
    oc_carrier_id = fields.Many2one('res.partner', string="Carrier")
