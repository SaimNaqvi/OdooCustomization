from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    subscription_ids = fields.One2many(
        comodel_name='sale.subscription',
        inverse_name='partner_id',
        string='Subscriptions'
    )

    subscription_count = fields.Integer(
        compute='_compute_subscription_count',
        store=True
    )

    @api.depends('subscription_ids')
    def _compute_subscription_count(self):
        for partner in self:
            partner.subscription_count = len(partner.subscription_ids)


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    partner_id = fields.Many2one('res.partner', string='Customer', domain="[('title', '=', 'Student')]")
