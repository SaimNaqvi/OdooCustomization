from datetime import datetime, timedelta
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_tier = fields.Selection([
        ('bronze', 'Bronze'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum')
    ], string="Customer Tier", compute="_compute_customer_tier", store=True)

    is_carrier = fields.Boolean(string="Is Carrier", store=True)

    @api.depends('sale_order_ids','pos_order_ids')
    def _compute_customer_tier(self):
        six_months_ago = datetime.now() - timedelta(days=180)
        for partner in self:
            # Sales Order Sales
            if not partner.name or not partner.customer_rank:
                continue
            sale_orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('date_order', '>=', six_months_ago),
                ('state', 'in', ['sale', 'done']),
            ])
            sales_amount = sum(order.amount_total for order in sale_orders)

            # POS Sales
            pos_orders = self.env['pos.order'].search([
                ('partner_id', '=', partner.id),
                ('date_order', '>=', six_months_ago),
                ('state', 'in', ['paid','done']),
            ])
            pos_amount = sum(order.amount_total for order in pos_orders)

            total_sales_amount = sales_amount + pos_amount

            # Determine Customer Tier
            if total_sales_amount <= 1000:
                tier = 'bronze'
            elif 1000 < total_sales_amount <= 3000:
                tier = 'gold'
            else:
                tier = 'platinum'

            # Update the `customer_tier` field
            partner.customer_tier = tier

            # Concatenate Customer Tier with Name
            tier_label = dict(self._fields['customer_tier'].selection).get(tier, '')

            # Remove any existing tier suffix (e.g., [Bronze], [Gold], [Platinum])
            if "[" in partner.name and "]" in partner.name:
                partner.name = partner.name.split(' [')[0].strip()

            # Append the current tier only if it's different
            if tier_label:
                partner.name = f"{partner.name} [{tier_label}]"
