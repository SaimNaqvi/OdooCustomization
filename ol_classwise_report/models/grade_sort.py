from odoo import models, fields, api


class StudentGradeSort(models.Model):
    _inherit = "res.partner"

    # grade_no = fields.Char(string="Grade Rank", store=True)