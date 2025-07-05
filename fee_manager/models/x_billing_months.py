from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime


class BillingMonth(models.Model):
    _name = 'x_billing_months'
    _description = "billing.months"
    _rec_name = 'x_name'

    x_name = fields.Char(string="Name")
