from odoo import api, models, modules, fields
import urllib.request
import urllib.parse
import json
import logging
import requests
import re

_logger = logging.getLogger(__name__)


class EnrollmentHistories(models.Model):
    _name = 'enrollment.histories'

    history_id = fields.Integer(string='Enrollment History ID')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    status = fields.Char(string='Status')
    grade_level = fields.Char(string='Grade Level')
    school_name = fields.Char(string='School Name')
    notes = fields.Char(string='Notes')
    enrollment_history_id = fields.Many2one('res.partner', string='Student')
