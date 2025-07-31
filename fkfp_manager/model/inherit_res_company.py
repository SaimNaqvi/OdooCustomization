# models/res_company.py
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_for_project = fields.Boolean(string='Is for Project?')
    is_main_company = fields.Boolean(string="Is Main Company")