from odoo import models, fields


class ProjectStatus(models.Model):
    _name = 'project.status'
    _description = 'Project Status'
    _rec_name = 'status_name'

    status_name = fields.Char(string='Status', store=True)
