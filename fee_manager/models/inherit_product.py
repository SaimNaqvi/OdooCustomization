from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime


class InheritProduct(models.Model):
    _inherit = "product.template"
    x_studio_many2many_field_E1EQQ = fields.Many2many(
        'x_billing_months',
        'x_product_product_x_billing_months_rel',
        'product_product_id',
        'x_billing_months_id',
        string='Billing Months', store=True, copy=True)
    x_studio_subscription_templates = fields.Many2many(
        'sale.subscription.template',
        'x_product_product_sale_subscription_template_rel',
        'product_product_id',
        'sale_subscription_template_id',
        string='Subscription Templates', store=True, copy=True)
