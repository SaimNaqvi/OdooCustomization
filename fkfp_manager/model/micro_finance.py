from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    small_business = fields.Integer(string="How much loan do you need to setup a small business ?", store=True)
    business_plan = fields.Char(string="What is your business plan ?", store=True)
    return_money = fields.Char(string="How will you return the money ?", store=True)
    amount = fields.Char(string="How much amount do you return?", store=True)
