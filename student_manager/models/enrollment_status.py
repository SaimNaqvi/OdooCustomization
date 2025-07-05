from odoo import models, fields


class EnrollmentStatus(models.Model):
    _name = 'enrollment.status'
    _description = 'Enrollment Status'

    name = fields.Char(string="Status", store=True)
