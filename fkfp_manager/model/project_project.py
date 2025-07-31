from odoo import models, fields


class ProjectProject(models.Model):
    _name = 'project.project'
    _description = 'Projects'

    project_name = fields.Char(string='project', store=True)
