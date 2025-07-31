from odoo import models, fields
from zeep.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fob_point = fields.Many2one('fob.point', string="FOB Point")
    ship_via = fields.Many2one('ship.via', string="Ship Via")

    # def button_confirm(self):
    #     res = super(PurchaseOrder, self).button_confirm()
    #     self._create_picking()
    #     return res
    #
    # def _create_picking(self):
    #     for order in self:
    #         picking_type = order.picking_type_id
    #         default_location_src = picking_type.default_location_src_id.id if picking_type and picking_type.default_location_src_id else False
    #
    #         # Fallback logic
    #         if not default_location_src:
    #             # Aap ek default location ka ID manually set kar sakte hain, ya phir error raise kar sakte hain
    #             # Example:
    #             default_location_src = self.env.ref('stock.stock_location_stock').id  # Default Stock Location
    #
    #             # Agar aap chahte hain ke error raise ho:
    #             # raise ValidationError("The picking type has no default source location. Please configure it properly.")
    #
    #         # GRN create karne ka logic
    #         picking = self.env['stock.picking'].create({
    #             'partner_id': order.partner_id.id,
    #             'picking_type_id': picking_type.id,
    #             'location_id': default_location_src,
    #             'location_dest_id': order.partner_id.property_stock_supplier.id,
    #             'origin': order.name,
    #             'move_ids_without_package': [(0, 0, {
    #                 'product_id': line.product_id.id,
    #                 'name': line.name,
    #                 'product_uom_qty': line.product_qty,
    #                 'product_uom': line.product_uom.id,
    #                 'location_id': default_location_src,
    #                 'location_dest_id': order.partner_id.property_stock_supplier.id,
    #                 'purchase_line_id': line.id,
    #             }) for line in order.order_line],
    #         })
    #         picking.action_confirm()
