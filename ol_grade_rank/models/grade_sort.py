from odoo import models, fields, api


class StudentGradeSort(models.Model):
    _inherit = "res.partner"

    grade_no = fields.Integer(string="Grade Rank", store=True)