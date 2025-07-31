from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    own_house = fields.Boolean(string="Do you have your own house?", store=True)
    house_rooms = fields.Integer(string="How many rooms in your house?", store=True)
    has_toilet = fields.Boolean(string="Do you have a toilet in your house?", store=True)
    livestock_count = fields.Integer("How many livestock do you own?", store=True)
    kaccha_pakka = fields.Char(string="House Kaccha or Pakka", store=True)
    own_property = fields.Char(string="Do you own any other property?", store=True)
    monthly_income = fields.Integer(string='Monthly Total Income', store=True)
    monthly_expense = fields.Integer(string='Monthly Total Expense', store=True)
    average_annual = fields.Integer(string='Average Annual Income', store=True)
    debit = fields.Integer(string='How much debit do you have?', store=True)
    interest = fields.Integer(string='How much interest do you pay on your debit?', store=True)
    source = fields.Char(string='By what source do you pay interest?', store=True)
    monthly_self = fields.Integer(string="Monthly Self Income", store=True)
    family_income = fields.Integer(string="Monthly Family Income", store=True)
    total_area = fields.Char(string="Total area of land for crop", store=True)
    crop_name = fields.Char(string="Name of Crop", store=True)
    land_owner = fields.Char(string="Land Owner Name", store=True)
    owner_contact = fields.Char(string="Land owner contact detail", store=True)
