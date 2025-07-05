# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, modules, fields, _
import urllib.request
import urllib.parse
import json
import logging
import requests
import re
from datetime import datetime, timedelta
from odoo.exceptions import UserError

from datetime import datetime
from retry import retry
from requests.exceptions import HTTPError, ConnectionError
from collections import defaultdict
from . import update_parent_records

file_path = 'custom_addons/student_manager/models/images.txt'
_logger = logging.getLogger(__name__)

BASE_URL_STUDENTS = 'https://api.factsmgt.com/Students'
BASE_URL_PEOPLE = 'https://api.factsmgt.com/People'
BASE_URL_ADDRESS = 'https://api.factsmgt.com/people/Address'
BASE_URL_HOMEROOM = 'https://api.factsmgt.com/Classes/students'
BASE_URL_FAMILIES = 'https://api.factsmgt.com/families'
BASE_URL_RELATION = 'https://api.factsmgt.com/people/ParentStudent'
BASE_URL_ENROLLMENT = 'https://api.factsmgt.com/students/EnrollmentHistories'
BASE_URL_USERDEFINEDDATA = 'https://api.factsmgt.com/UserDefinedData'
HEADERS = {
    'Ocp-Apim-Subscription-Key': '03f001e670f14071acb128360118bf97',
    'Facts-Api-Key': '0UP1qsO4hH3U6QQKvK7KWszA631/e6YcVTNBC2QP46qIQg7NVgDYoXYqbuuj35lfSALndtkKJwWnqrH9r6xKHaKqjmpDK3XdmkGvHE1P1Xg=',
}

VIEW_TYPES = [
    ('Christian', 'Christian'),
    ('Islam', 'Islam'),
    ('hindu', 'Hindu'),
    ('sikh', 'Sikh'),
    ('Ahmedi', 'Ahmedi'),
]
relationship_types = [
    ('Aunt', 'Aunt'),
    ('Brother', 'Brother'),
    ('Donor', 'Donor'),
    ('Father', 'Father'),
    ('Friend', 'Friend'),
    ('Grand parent', 'Grand parent'),
    ('Guardian', 'Guardian'),
    ('Mother', 'Mother'),
    ('Sister', 'Sister'),
    ('Spouse', 'Spouse'),
    ('Step father', 'Step father'),
    ('Step mother', 'Step mother'),
    ('Uncle', 'Uncle'),
    ('Other', 'Other'),
]
class_selection = [('nur', 'Nur'), ('prep', 'Prep'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
                   ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')]

section_types = [('earth', 'Earth'), ('mars', 'Mars'), ('jupiter', 'Jupiter'), ('Red', 'Red')]

parent_salutation_selection = [('Dr.', 'Dr.'), ('Miss', 'Miss'), ('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Sir.', 'Sir.')]

test_status = [('Pass', "Pass"), ('Fail', "Fail"), ('Dropped', 'Dropped')]


class StudentManager(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char(string="First Name", store=True)
    last_name = fields.Char(string="Last Name", store=True)
    is_student = fields.Boolean(string="is Student", store=True)
    is_parent = fields.Boolean(string="is Parent", store=True)
    # is_staff = fields.Boolean(string="is staff", store=True)

    title = fields.Many2one('res.partner.title', string="Type")

    ####### facts fields #####
    facts_id = fields.Integer(string="Facts Id", store=True)
    facts_nickname = fields.Char(string="Facts Nick Name", store=True)
    facts_udid = fields.Char(string="Facts UDID", store=True)
    # facts_udid_as_integer = fields.Integer(string="Facts UDID as Integer", compute="_compute_facts_udid_as_integer",
    #                                        store=True)
    roll_no = fields.Integer(string='Roll Number', store=True)
    student_code = fields.Char(string='Student Code', store=True)
    reg_number = fields.Char(string='Registration Number', store=True)

    ###### my custom fields #####
    x_studio_parent_id = fields.Integer(string="Parent Id", store=True, readonly=True)
    person_student_id = fields.Integer(string="Person Student ID", store=True)
    current_grade = fields.Char(string="Current Grade", store=True)
    current_grade_selection = fields.Selection(class_selection, string="Current Grade", store=True)
    next_grade = fields.Char(string="Next Grade", store=True)
    next_grade_selection = fields.Selection(class_selection, string="Next Grade", store=True)
    current_enroll_status = fields.Many2one('enrollment.status', string="Current Enrollment Status", store=True)
    next_enroll_status = fields.Many2one('enrollment.status', string="Next Enrollment Status", store=True)
    # homeroom = fields.Char(string='Homeroom', compute='_compute_homeroom', store=True)
    homeroom = fields.Char(string='Homeroom', store=True)
    new_homeroom = fields.Selection(section_types, string="Homeroom", store=True)

    update_homeroom_button = fields.Boolean(string='Update Homeroom', store=True)
    current_school = fields.Many2one('res.branch', string='Current School', store=True)
    student_relationship_ids = fields.One2many('relationship.info', 'student_id', string="Relationships", store=True)
    student_ids = fields.One2many('relationship.info', 'parent_id', string="Students", store=True)
    enrollment_histories_ids = fields.One2many('enrollment.histories', 'enrollment_history_id',
                                               string='Enrollment Histories', store=True)
    grade_section_display = fields.Char(string='Grade and Section', compute='_compute_grade_and_section_display',
                                        store=True)

    concession_comment = fields.Text(string="Student Concession", store=True)

    image_url_data = fields.Text(string='Image URL Data', help='Paste the image URL data from the text file.')
    date = fields.Date(string="Date")
    gender = fields.Selection([("male", "Male"), ("female", "Female"), ("other", "Other")], string="Gender")
    dob = fields.Date(string='Date of Birth')
    cnic = fields.Char(string="CNIC", store=True, copy=True)
    b_form = fields.Char(string="B-Form", store=True, copy=True)
    parent_name = fields.Char(string='Parent Name', store=True, readonly=True)
    # display_name = fields.Char(string="Display Name", store=True)
    full_name = fields.Char(string="Full Name", store=True, tracking=True)
    contact_address = fields.Char(compute='_compute_contact_address', string='Complete Address')
    next_school = fields.Many2one('res.branch', string='Next School', store=True)
    previous_school = fields.Char(string='Previous School', store=True)
    student_concessions = fields.One2many('student.concession', 'student_id', string='Concessions')

    religion = fields.Selection(VIEW_TYPES, string='Religion', store=True)
    old_RegistrationNo = fields.Integer(string='Old Registration No', store=True)
    board_roll_no = fields.Integer(string='Board Roll No', store=True)
    admission_date = fields.Date(string='Admission Date', store=True)
    test_date = fields.Date(string='Test Date', store=True)
    test_status = fields.Selection(test_status, string='Test Status', store=True)
    left_date = fields.Date(string='Left Date', store=True)

    admitted_class_name = fields.Char(string='Admitted Class', store=True)
    print = fields.Integer(string='Print', store=True)
    take_exam = fields.Integer(string='Take Exam', store=True)
    employee_id = fields.Integer(string='Employee ID', store=True)
    pastor_id = fields.Integer(string='Pastor ID', store=True)

    # Hostel Info  #
    hostel_id = fields.Integer(string='Hostel ID', store=True)
    hostel_code = fields.Integer(string='Hostel Code', store=True)
    hostel_concession = fields.Float(string='Hostel Concession', store=True)

    # Donor Info #
    donor_id = fields.Integer(string='Donor ID', store=True)
    donor_name = fields.Char(string='Donor Name', store=True)

    # parent info
    parent_occupation = fields.Char(string='Parent Occupation', store=True)
    parent_education = fields.Char(string='Parent Education', store=True)
    parent_salutation = fields.Selection(parent_salutation_selection, string='Salutation')

    # Dynamic One2many field for parents
    family_parent_ids = fields.One2many(
        'res.partner',
        'related_student_id',
        string="Parents",
        domain="[('is_parent', '=', True)]"
    )

    # Dynamic One2many field for students
    family_student_ids = fields.One2many(
        'res.partner',
        'related_parent_id',
        string="Students",
        domain="[('is_student', '=', True)]"
    )

    def _get_closed_stage_id(self):
        return self.env['sale.subscription.stage'].search([('name', '=', 'Closed')], limit=1).id

    def migrate_char_to_selection(self):
        records = self.search([('title', '=', 'Student')])
        for record in records:
            if record.homeroom:
                # Map old char values to new selection values
                if record.homeroom == 'Earth':
                    record.new_homeroom = 'Earth'
                elif record.homeroom == 'Mars':
                    record.new_homeroom = 'Mars'
                    print(record.new_homeroom)
                elif record.homeroom == 'Jupiter':
                    record.new_homeroom = 'Jupiter'
                elif record.homeroom == 'Red':
                    record.new_homeroom = 'Red'

    def migrate_class_to_selection(self):
        records = self.search([('title', '=', 'Student')])
        for record in records:
            if record.current_grade:
                # Map old char values to new selection values
                if record.current_grade == 'Nur' or record.current_grade == 'NUR':
                    record.current_grade_selection = 'nur'
                if record.current_grade == 'Prep' or record.current_grade == 'PREP':
                    record.current_grade_selection = 'prep'
                if record.current_grade == '1':
                    record.current_grade_selection = '1'
                elif record.current_grade == '2':
                    record.current_grade_selection = '2'
                elif record.current_grade == '3':
                    record.current_grade_selection = '3'
                elif record.current_grade == '4':
                    record.current_grade_selection = '4'
                elif record.current_grade == '5':
                    record.current_grade_selection = '5'
                elif record.current_grade == '6':
                    record.current_grade_selection = '6'
                elif record.current_grade == '7':
                    record.current_grade_selection = '7'
                elif record.current_grade == '8':
                    record.current_grade_selection = '8'
                elif record.current_grade == '9':
                    record.current_grade_selection = '9'
                elif record.current_grade == '10':
                    record.current_grade_selection = '10'
            if record.next_grade:
                # Map old char values to new selection values
                if record.current_grade == 'Nur' or record.current_grade == 'NUR':
                    record.current_grade_selection = 'Nur'
                if record.current_grade == 'Prep' or record.current_grade == 'PREP':
                    record.current_grade_selection = 'Prep'
                if record.next_grade == '1':
                    record.next_grade_selection = '1'
                elif record.next_grade == '2':
                    record.next_grade_selection = '2'
                elif record.next_grade == '3':
                    record.next_grade_selection = '3'
                elif record.next_grade == '4':
                    record.next_grade_selection = '4'
                elif record.next_grade == '5':
                    record.next_grade_selection = '5'
                elif record.next_grade == '6':
                    record.next_grade_selection = '6'
                elif record.next_grade == '7':
                    record.next_grade_selection = '7'
                elif record.next_grade == '8':
                    record.next_grade_selection = '8'
                elif record.next_grade == '9':
                    record.next_grade_selection = '9'
                elif record.next_grade == '10':
                    record.next_grade_selection = '10'

    @api.model
    def default_get(self, fields_list):
        defaults = super(StudentManager, self).default_get(fields_list)
        # Assuming 'admission' is the name of the enrollment status you want to set as default
        admission_status = self.env['enrollment.status'].search([('name', '=', 'Registration')], limit=1)
        is_student_view = self._context.get('is_student_view', False)
        current_school = self.env['res.branch'].search([('id', '=', self.env.context.get('allowed_branch_ids', None))])
        if current_school:
            defaults['current_school'] = current_school.id
        if is_student_view:
            title = self.env['res.partner.title'].search([('name', '=', 'Student')], limit=1)
            defaults['title'] = title
        is_parent_view = self._context.get('is_parent_view', False)
        if is_parent_view:
            title = self.env['res.partner.title'].search([('name', '=', 'Parent')], limit=1)
            defaults['title'] = title
        is_company_view = self._context.get('is_company_view', False)
        if is_company_view:
            title = self.env['res.partner.title'].search([('name', '=', 'Family')], limit=1)
            defaults['title'] = title
        if admission_status:
            defaults['current_enroll_status'] = admission_status.id
        return defaults

    def grade_and_section_display(self):
        section_dict = dict(self.fields_get(allfields=['new_homeroom'])['new_homeroom']['selection'])
        records = self.search([('title', '=', 'Student')])
        for partner in records:
            if partner.new_homeroom:
                capitalized_section = section_dict.get(partner.new_homeroom, '')
                partner.grade_section_display = f"Class {partner.current_grade_selection} {capitalized_section}"
            elif partner.current_grade_selection:
                partner.grade_section_display = f"Class {partner.current_grade_selection}"
            else:
                partner.grade_section_display = ''

    @api.depends('current_grade_selection', 'new_homeroom')
    def _compute_grade_and_section_display(self):
        for partner in self:
            if partner.current_grade_selection and partner.new_homeroom:
                partner.grade_section_display = f"Class {partner.current_grade_selection} {partner.new_homeroom}"
            elif partner.current_grade_selection:
                partner.grade_section_display = f"Class {partner.current_grade_selection}"
            else:
                partner.grade_section_display = ''
            if partner.current_grade_selection and partner.current_enroll_status:
                enrollment_status = self.env['enrollment.status'].browse(partner.current_enroll_status.id)
                if partner.current_grade_selection == 'nur' or partner.current_grade_selection == 'Nur':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Admission')])
                    next_grade = 'prep'
                    partner.next_grade_selection = next_grade
                    partner.next_enroll_status = next_enrollment_status.id
                elif partner.current_grade_selection == 'prep' or partner.current_grade_selection == 'Prep':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Admission')])
                    next_grade = 1
                    partner.next_grade_selection = str(next_grade)
                    partner.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Registration':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Admission')])
                    next_grade_number = int(partner.current_grade_selection)
                    partner.next_grade_selection = str(next_grade_number)
                    partner.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Withdrawn':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Withdrawn')])
                    partner.next_grade = ''
                    partner.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Graduate':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Graduate')])
                    partner.next_grade = ''
                    partner.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Dropped':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Dropped')])
                    partner.next_grade = ''
                    partner.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Admission':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Enrolled')])
                    partner.next_grade_selection = partner.current_grade_selection
                    partner.next_enroll_status = next_enrollment_status.id
                else:
                    next_grade_number = int(partner.current_grade_selection) + 1
                    partner.next_grade_selection = str(next_grade_number)
                    partner.next_enroll_status = enrollment_status.id

    @api.model
    def create(self, vals):
        context = self.env.context
        is_student_view = context.get('is_student_view', False)
        if is_student_view:
            branch = self.env['res.branch'].browse(vals.get('branch_id'))
            if branch:
                set_student_code = branch.set_student_code

                # Get the last student code for the branch
                last_student = self.search([
                    ('branch_id', '=', branch.id),
                    ('is_student', '=', True),
                    ('reg_number', '!=', False)
                ], order='reg_number desc', limit=1)

                if last_student and last_student.reg_number:
                    last_student_code = int(last_student.reg_number)
                else:
                    last_student_code = set_student_code

                new_reg_number = int(last_student_code) + 1
                vals['reg_number'] = new_reg_number
        if vals.get('first_name'):
            vals['first_name'] = vals.get('first_name')
        if vals.get('last_name'):
            vals['last_name'] = vals.get('last_name')
        if vals.get('first_name') or vals.get('last_name'):
            first_name = vals.get('first_name', '')
            last_name = vals.get('last_name', '')
            if first_name and last_name:
                vals['name'] = f"{first_name} {last_name}"
                vals['full_name'] = f"{first_name} {last_name}"
            elif first_name:
                vals['name'] = first_name
                vals['full_name'] = first_name
            elif last_name:
                vals['name'] = last_name
                vals['full_name'] = last_name
        if vals.get('name'):
            vals['name'] = vals.get('name')
            vals['full_name'] = vals.get('name')
        student = super(StudentManager, self).create(vals)
        if vals.get('current_enroll_status') or vals.get('current_grade'):
            self.create_enrollment_history(student)
        # Fetch the selected fee charges
        product = self.env['product.product'].sudo().search([('name', '=', 'Registration Fee')], limit=1)
        # Calculate dates
        invoice_date = datetime.now()
        invoice_date_due = invoice_date + timedelta(days=9)
        billing_month = invoice_date.strftime('%b-%y')
        # Ensure the product has an income account
        account_id = product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id
        if is_student_view:
            try:
                invoice = self.env['account.move'].sudo().create({
                    'move_type': 'out_invoice',
                    'partner_id': student.id,
                    'invoice_date': invoice_date,
                    'invoice_date_due': invoice_date_due,
                    'billingMonth': billing_month,
                    'branch_id': branch.id,
                    'invoice_line_ids': [(0, 0, {
                        'product_id': product.id,
                        'account_id': account_id,
                        'price_unit': product.list_price,
                        'name': product.name,
                        'quantity': 1,
                    })]
                })
            except Exception as e:
                _logger.error('Failed to create invoice: %s', e)
                raise

        return student

    @api.onchange('first_name', 'last_name')
    def compute_name(self):
        if self.name:
            first_name = str(self.first_name) if self.first_name else ''
            last_name = str(self.last_name) if self.last_name else ''
            self.full_name = ' '.join([first_name, last_name])
            self.name = ' '.join([first_name, last_name])

    @api.onchange('current_grade_selection', 'current_enroll_status')
    def update_next_grade_and_status(self):
        for record in self:
            if record.current_grade_selection and record.current_enroll_status:
                enrollment_status = self.env['enrollment.status'].browse(record.current_enroll_status.id)
                if record.current_grade_selection == 'nur' or record.current_grade_selection == 'Nur':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Admission')])
                    next_grade = 'prep'
                    record.next_grade_selection = next_grade
                    record.next_enroll_status = next_enrollment_status.id
                elif record.current_grade_selection == 'prep' or record.current_grade_selection == 'Prep':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Admission')])
                    next_grade = 1
                    record.next_grade_selection = str(next_grade)
                    record.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Registration':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Admission')])
                    next_grade_number = int(record.current_grade_selection)
                    record.next_grade_selection = str(next_grade_number)
                    record.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Withdrawn':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Withdrawn')])
                    record.next_grade = ''
                    record.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Graduate':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Graduate')])
                    record.next_grade = ''
                    record.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Dropped':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Dropped')])
                    record.next_grade = ''
                    record.next_enroll_status = next_enrollment_status.id
                elif enrollment_status.name == 'Admissions' or enrollment_status.name == 'Admission':
                    next_enrollment_status = self.env['enrollment.status'].search([('name', '=', 'Enrolled')])
                    record.next_grade_selection = record.current_grade_selection
                    record.next_enroll_status = next_enrollment_status.id


                else:
                    next_grade_number = int(record.current_grade_selection) + 1
                    record.next_grade_selection = str(next_grade_number)
                    record.next_enroll_status = enrollment_status.id

    @api.model
    def clean_up_names(self):
        partners_with_whitespace = self.search([('is_student', '=', True)])
        for partner in partners_with_whitespace:
            vals = {}
            if partner.first_name:
                vals['first_name'] = partner.first_name.strip()
            if partner.last_name:
                vals['last_name'] = partner.last_name.strip()
            partner.write(vals)

    @api.depends('family_parent_ids')
    def _compute_contact_address(self):
        for family in self:
            # Check if there are parents in the family
            if family.family_parent_ids:
                # Assuming that family_parent_ids is an ordered One2many field
                first_parent = family.family_parent_ids[0]
                # Update contact_address based on the first parent's address
                address_parts = []
                if first_parent.street:
                    address_parts.append(first_parent.street)
                if first_parent.zip:
                    address_parts.append(first_parent.zip)
                if first_parent.city:
                    address_parts.append(first_parent.city)
                family.contact_address = ", ".join(address_parts)
                # get parent from family
                get_parent = family.family_parent_ids[0]
                family.write({
                    'display_name': get_parent.display_name,
                    'phone': get_parent.phone if get_parent.phone else get_parent.mobile
                })
            else:
                family.contact_address = False

    def _compute_full_name(self):
        all_students = self.search([('is_student', '=', True)])
        for partner in all_students:
            if partner.last_name:
                partner.full_name = "{} {}".format(partner.first_name, partner.last_name)
                partner.name = "{} {}".format(partner.first_name, partner.last_name)
            else:
                partner.full_name = partner.first_name
                partner.name = partner.first_name

    def _compute_parent_name(self):
        for partner in self:
            # Fetch the parent's name from the first record in student_relationship_ids
            parent_name = partner.student_relationship_ids and partner.student_relationship_ids[0].parent_id.name
            partner.parent_name = parent_name

    @api.depends('is_parent', 'is_student')
    def _compute_related_fields(self):
        for record in self:
            if record.is_parent:
                record.related_student_id = False
            elif record.is_student:
                record.related_parent_id = False

    related_parent_id = fields.Many2one('res.partner', string="Related Parent", compute='_compute_related_fields',
                                        store=True)
    related_student_id = fields.Many2one('res.partner', string="Related Student", compute='_compute_related_fields',
                                         store=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(StudentManager, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu)
        if toolbar:
            actions_in_toolbar = res['toolbar'].get('action')
            if actions_in_toolbar:
                if not self._context.get('is_student_view', False):
                    approve_button_id = self.env.ref('student_manager.action_sync_records').id or False
                    approve_inserting_parent_name = self.env.ref(
                        'student_manager.action_assign_parent_name').id or False
                    # sync_parent_record_id = self.env.ref('student_manager.action_sync_parent_records').id or False
                    for button in res.get('toolbar', {}).get('action', []):
                        if approve_button_id and button['id'] == approve_button_id:
                            res['toolbar']['action'].remove(button)
                        if approve_inserting_parent_name and button['id'] == approve_inserting_parent_name:
                            res['toolbar']['action'].remove(button)
                        # if display_name_button_id and button['id'] == display_name_button_id:
                        #     res['toolbar']['action'].remove(button)
                else:
                    approve_button_id = self.env.ref('student_manager.action_sync_parent_records').id or False
                    for button in res.get('toolbar', {}).get('action', []):
                        if approve_button_id and button['id'] == approve_button_id:
                            res['toolbar']['action'].remove(button)
        if view_type == 'pivot' and self.env.context.get('allowed_branch_ids'):
            res['fields']['branch_id']['context'] = {}
        return res

    def open_student(self):
        self.ensure_one()
        return {
            'name': _("Student"),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    @api.model
    def update_cnic(self):
        try:
            BASE_URL = BASE_URL_USERDEFINEDDATA
            response_user_define_data = requests.get(BASE_URL, headers=HEADERS)
            if response_user_define_data.status_code == 200:
                response_user_define_data.raise_for_status()
                user_define_data = response_user_define_data.json()
                all_parent_record = []
                max_pages = user_define_data.get('pageCount')  # Maximum number of pages to fetch
                page = 1
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'danger',
                        'title': 'Error!',
                        'message': f"Not Responding from server status code is {response_user_define_data.status_code}",
                        'sticky': False,
                    },
                }
            all_parent = self.env['res.partner'].search([('is_parent', '=', True)])
            while BASE_URL and page <= max_pages:
                try:
                    response_user_define_data = self.make_request(BASE_URL)
                    user_define_data = response_user_define_data
                except Exception as e:
                    _logger.error(f"Error fetching data from {BASE_URL}: {e}")
                    return
                for data in user_define_data.get('results', []):
                    _parent_facts_id = data.get('linkedId')
                    _parent_cnic = data.get('data')

                    for parent in all_parent:
                        if (not parent.cnic) or (parent.cnic != _parent_cnic and parent.facts_id == _parent_facts_id):
                            parent.update({'cnic': _parent_cnic})
                            all_parent_record.append(parent)
                BASE_URL = user_define_data.get('nextPage')  # Get the next page URL
                page += 1
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Success!',
                    'message': f'{len(all_parent_record)} individuals fetched from {page - 1} pages.',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.exception('Error while fetching and creating individuals: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Error!',
                    'message': str(e),
                    'sticky': False,
                },
            }

    def update_dob_gender(self):
        all_records = self.env['res.partner'].search([('is_company', '=', False)])
        try:
            for data in all_records:
                if data.facts_id != 0:
                    response_people = self.make_request(f'https://api.factsmgt.com/people/{data.facts_id}/Demographic')
                    data_people = response_people
                    if data_people.get('personId', None):
                        gender = data_people.get('gender', None)
                        gender_odoo_value = None
                        if gender == "Male":
                            gender_odoo_value = "male"
                        elif gender == "Female":
                            gender_odoo_value = "female"
                        else:
                            gender_odoo_value = "other"
                        date_of_birth_str = data_people.get('birthdate', None)
                        if date_of_birth_str:
                            date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%dT%H:%M:%SZ").date()
                        else:
                            date_of_birth = None
                        # Update the record with the new data
                        data.write({
                            'gender': gender_odoo_value,
                            'dob': date_of_birth,
                            # Add other fields you want to update
                        })

        except Exception as e:
            _logger.exception('Error while fetching and creating individuals: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Error!',
                    'message': str(e),
                    'sticky': False,
                },
            }

    def update_single_dob_gender(self):
        for data in self:
            if data.facts_id != 0:
                response_people = self.make_request(f'https://api.factsmgt.com/people/{data.facts_id}/Demographic')
                data_people = response_people
                if data_people.get('personId', None):
                    gender = data_people.get('gender', None)
                    gender_odoo_value = None
                    if gender == "Male":
                        gender_odoo_value = "male"
                    elif gender == "Female":
                        gender_odoo_value = "female"
                    else:
                        gender_odoo_value = "other"
                    date_of_birth_str = data_people.get('birthdate', None)
                    if date_of_birth_str:
                        date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%dT%H:%M:%SZ").date()
                    else:
                        date_of_birth = None
                    # Update the record with the new data
                    data.write({
                        'gender': gender_odoo_value,
                        'dob': date_of_birth,
                        # Add other fields you want to update
                    })

    @api.model
    def update_branches(self):
        pass

    def sync_data(self):
        # Call each function in the desired order
        # self.get_students()
        # self.get_individuals()
        # self.get_families_details()
        # self.get_relations()
        # self.populate_student_ids_in_relationships()
        self.get_person_family()
        # self.button_update_relationships()
        # self.get_enrollment_history()
        # self.update_enrollment_history()

    @retry(ConnectionError, delay=2, backoff=2, max_delay=10, tries=5)
    def make_request(self, url):
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise requests.exceptions.HTTPError(f"Unexpected status code: {response.status_code}")
        except ConnectionError as e:
            raise ConnectionError(f"Connection error: {e}")
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(f"HTTP error: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def update_all_data(self):
        all_students = self.env['res.partner'].search(['&', ('is_student', '=', True), ('facts_id', '!=', 0)])
        all_parents = self.env['res.partner'].search(['&', ('is_parent', '=', True), ('facts_id', '!=', 0)])
        if all_parents:
            update_parent_data = self.update_all_parent_record(all_parents)
        for rec in all_students:
            if rec.person_student_id:
                response_student = self.make_request(
                    f'https://api.factsmgt.com/Students/{rec.person_student_id}')
                student_data = response_student
                academic_student_data = student_data.get('school')
                if student_data:
                    if student_data.get('personStudentId', None):
                        if rec.person_student_id != student_data.get('personStudentId'):
                            rec.person_student_id = student_data.get('personStudentId')
                    if student_data.get('studentId', None):
                        if rec.facts_id != student_data.get('studentId'):
                            rec.facts_id = student_data.get('studentId')
                    if student_data.get('schoolCode', None):
                        if rec.current_school != student_data.get('schoolCode'):
                            rec.current_school = student_data.get('schoolCode')
                    if academic_student_data.get('status', None):
                        status_name = academic_student_data.get('status')
                        if status_name:
                            status = self.env['enrollment.status'].search([('name', '=', status_name)], limit=1)
                            if not status:
                                status = self.env['enrollment.status'].create({'name': status_name})
                            if rec.current_enroll_status.name != academic_student_data.get('status'):
                                rec.current_enroll_status = status.id
                    if academic_student_data.get('gradeLevel', None):
                        if rec.current_grade != academic_student_data.get('gradeLevel'):
                            rec.current_grade = academic_student_data.get('gradeLevel')
                    if academic_student_data.get('nextStatus', None):
                        status_name = academic_student_data.get('nextStatus')
                        if status_name:
                            status = self.env['enrollment.status'].search([('name', '=', status_name)], limit=1)
                            if not status:
                                status = self.env['enrollment.status'].create({'name': status_name})
                            if rec.next_enroll_status.name != academic_student_data.get('nextStatus'):
                                rec.next_enroll_status = status.id
                    if academic_student_data.get('nextGradeLevel', None):
                        if rec.next_grade != academic_student_data.get('nextGradeLevel'):
                            rec.next_grade = academic_student_data.get('nextGradeLevel')
                response_general_data = self.make_request(f'https://api.factsmgt.com/People/{rec.facts_id}')
                student_general_data = response_general_data
                if student_general_data:
                    if student_general_data.get('firstName', None):
                        if rec.first_name != student_general_data.get('firstName'):
                            rec.first_name = student_general_data.get('firstName')
                    if student_general_data.get('lastName', None):
                        if rec.last_name != student_general_data.get('lastName', None):
                            rec.last_name = student_general_data.get('lastName')
                    if student_general_data.get('email', None):
                        if rec.email != student_general_data.get('email', None):
                            rec.email = student_general_data.get('email', None)
                    if student_general_data.get('email2', None):
                        if rec.email != student_general_data.get('email2', None):
                            rec.email = rec.email + "," + student_general_data.get('email2', None)
                    if student_general_data.get('homePhone', None):
                        if rec.phone != student_general_data.get('homePhone', None):
                            rec.phone = student_general_data.get('homePhone', None)
                    if student_general_data.get('cellPhone', None):
                        if rec.mobile != student_general_data.get('cellPhone', None):
                            rec.mobile = student_general_data.get('cellPhone', None)
                addressId = student_general_data.get('addressID', None)
                if addressId != 0 and addressId is not None:
                    response_address_data = self.make_request(f'https://api.factsmgt.com/people/Address/{addressId}')
                    address_data = response_address_data
                    if address_data:
                        if address_data.get('address1', None):
                            if rec.street != address_data.get('address1', None):
                                rec.street = address_data.get('address1')
                        if address_data.get('address2', None):
                            if rec.street2 != address_data.get('address2'):
                                rec.street2 = address_data.get('address2', None)
                        if address_data.get('city', None):
                            if rec.city != address_data.get('city', None):
                                rec.city = address_data.get('city', None)
                        if address_data.get('country') == "PAK" or address_data.get('country') == "Pakistan":
                            if rec.country_id != address_data.get('country'):
                                country_code = 'PK'
                                get_country_id = self.env['res.country'].search([('code', '=', country_code)]).id
                                rec.country_id = get_country_id
                        if address_data.get('zip', None):
                            if rec.zip != address_data.get('zip', None):
                                rec.zip = address_data.get('zip', None)
                response_homeroom = self.make_request(f'{BASE_URL_HOMEROOM}/{rec.facts_id}')
                data_homeroom = response_homeroom
                list_of_data_homeroom = data_homeroom.get('results', [])
                if list_of_data_homeroom:
                    list_of_data_homeroom = list_of_data_homeroom[-1]
                    new_section = list_of_data_homeroom.get('section', None)
                    existing_string = rec.homeroom
                    if existing_string:
                        old_homeroom = existing_string.split('-')
                        if len(old_homeroom) > 1:
                            old_section = old_homeroom[1]
                            if old_section != new_section:
                                existing_string = old_homeroom[0]
                                rec.homeroom = existing_string + '-' + new_section if new_section else existing_string + '-' + old_section
                for relationship in rec.student_relationship_ids:
                    parent_id = relationship.parent_id.facts_id
                    student_id = rec.facts_id
                    try:
                        api_url = f'https://api.factsmgt.com/people/ParentStudent/parent/{parent_id}/student/{student_id}'
                        relation_data = self.make_request(api_url)
                        if relation_data is not None:
                            self._update_relation_in_odoo(relationship, relation_data)
                        else:
                            # Handle 404: Record has been deleted, unlink the relationship in Odoo
                            relationship.unlink()
                    except Exception as e:
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'type': 'danger',
                                'title': 'Error!',
                                'message': f"Request failed for student_id={student_id}, parent_id={parent_id}: {e}",
                                'sticky': False,
                            },
                        }
                rec.update_user_define_records()
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Record is not Updated!',
                        'message': str("Person Student Id is Missing..."),
                        'sticky': False,
                    },
                }
        self.get_relations()
        self.update_dob_gender()
        self.update_enrollment_histories()
        self.update_cnic()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': 'Record Updated!',
                'message': str("Record Updated Successfully..."),
                'sticky': False,
            },
        }

    def update_enrollment_histories(self):
        self.get_enrollment_history()
        self.update_enrollment_history()

    def _update_relation_in_odoo(self, relationship, relation_data):
        # Use the relation_data to update records in Odoo
        received_relationship = relation_data.get('relationship')
        relationship.write({
            'relationship_type': received_relationship.lower(),
            'custody': relation_data.get('custody'),
            'correspondence': relation_data.get('correspondence'),
            # Add other fields as needed...
        })

    def update_student_record(self, student_ids=None):
        if student_ids is None:
            for rec in self:
                if rec.person_student_id:
                    response_student = self.make_request(
                        f'https://api.factsmgt.com/Students/{rec.person_student_id}')
                    student_data = response_student
                    academic_student_data = student_data.get('school')
                    if student_data:
                        if student_data.get('personStudentId', None):
                            if rec.person_student_id != student_data.get('personStudentId'):
                                rec.person_student_id = student_data.get('personStudentId')
                        if student_data.get('studentId', None):
                            if rec.facts_id != student_data.get('studentId'):
                                rec.facts_id = student_data.get('studentId')
                        if student_data.get('schoolCode', None):
                            if rec.current_school != student_data.get('schoolCode'):
                                rec.current_school = student_data.get('schoolCode')
                        if academic_student_data.get('status', None):
                            status_name = academic_student_data.get('status')
                            if status_name:
                                status = self.env['enrollment.status'].search([('name', '=', status_name)], limit=1)
                                if not status:
                                    status = self.env['enrollment.status'].create({'name': status_name})
                                if rec.current_enroll_status != academic_student_data.get('status'):
                                    rec.current_enroll_status = status.id
                        if academic_student_data.get('gradeLevel', None):
                            if rec.current_grade != academic_student_data.get('gradeLevel'):
                                rec.current_grade = academic_student_data.get('gradeLevel')
                        if academic_student_data.get('nextStatus', None):
                            status_name = academic_student_data.get('nextStatus')
                            if status_name:
                                status = self.env['enrollment.status'].search([('name', '=', status_name)], limit=1)
                                if not status:
                                    status = self.env['enrollment.status'].create({'name': status_name})
                                if rec.next_enroll_status != academic_student_data.get('nextStatus'):
                                    rec.next_enroll_status = status.id
                        if academic_student_data.get('nextGradeLevel', None):
                            if rec.next_grade != academic_student_data.get('nextGradeLevel'):
                                rec.next_grade = academic_student_data.get('nextGradeLevel')
                    response_general_data = self.make_request(
                        f'https://api.factsmgt.com/People/{rec.facts_id}')
                    student_general_data = response_general_data
                    if student_general_data:
                        if student_general_data.get('firstName', None):
                            if rec.first_name != student_general_data.get('firstName'):
                                rec.first_name = student_general_data.get('firstName')
                        if student_general_data.get('lastName', None):
                            if rec.last_name != student_general_data.get('lastName', None):
                                rec.last_name = student_general_data.get('lastName')
                        if student_general_data.get('email', None):
                            if rec.email != student_general_data.get('email', None):
                                rec.email = student_general_data.get('email', None)
                        if student_general_data.get('email2', None):
                            if rec.email != student_general_data.get('email2', None):
                                rec.email = rec.email + "," + student_general_data.get('email2', None)
                        if student_general_data.get('homePhone', None):
                            if rec.phone != student_general_data.get('homePhone', None):
                                rec.phone = student_general_data.get('homePhone', None)
                        if student_general_data.get('cellPhone', None):
                            if rec.mobile != student_general_data.get('cellPhone', None):
                                rec.mobile = student_general_data.get('cellPhone', None)
                    addressId = student_general_data.get('addressID', None)
                    if addressId != 0 and addressId != None:
                        response_address_data = self.make_request(
                            f'https://api.factsmgt.com/people/Address/{addressId}')
                        address_data = response_address_data
                        if address_data:
                            if address_data.get('address1', None):
                                if rec.street != address_data.get('address1', None):
                                    rec.street = address_data.get('address1')
                            if address_data.get('address2', None):
                                if rec.street2 != address_data.get('address2'):
                                    rec.street2 = address_data.get('address2', None)
                            if address_data.get('city', None):
                                if rec.city != address_data.get('city', None):
                                    rec.city = address_data.get('city', None)
                            if address_data.get('state', None):
                                if rec.state_id.name != address_data.get('state', None):
                                    rec.state_id = self.env['res.country.state'].search(
                                        ['&', ('name', '=', address_data.get('state')), ('country_id', '=', 177)]).id
                            if address_data.get('country') == "PAK" or address_data.get('country') == "Pakistan":
                                if rec.country_id != address_data.get('country'):
                                    country_code = 'PK'
                                    get_country_id = self.env['res.country'].search([('code', '=', country_code)]).id
                                    rec.country_id = get_country_id

                            if address_data.get('zip', None):
                                if rec.zip != address_data.get('zip', None):
                                    rec.zip = address_data.get('zip', None)
                    response_homeroom = self.make_request(f'{BASE_URL_HOMEROOM}/{rec.facts_id}')
                    data_homeroom = response_homeroom
                    list_of_data_homeroom = data_homeroom.get('results', [])
                    if list_of_data_homeroom:
                        list_of_data_homeroom = list_of_data_homeroom[-1]
                        new_section = list_of_data_homeroom.get('section', None)
                        existing_string = rec.homeroom
                        if existing_string:
                            old_homeroom = existing_string.split('-')
                            if len(old_homeroom) > 1:
                                old_section = old_homeroom[1]
                                if old_section != new_section:
                                    existing_string = old_homeroom[0]
                                    rec.homeroom = existing_string + '-' + new_section if new_section else existing_string + '-' + old_section

                    # student_relations_id = self.env['res.partner'].search([('facts_id', '=', rec.facts_id)]).mapped(
                    #     'student_relationship_ids').mapped('parent_id.facts_id')
                    for relationship in rec.student_relationship_ids:
                        parent_id = relationship.parent_id.facts_id
                        student_id = rec.facts_id
                        try:
                            api_url = f'https://api.factsmgt.com/people/ParentStudent/parent/{parent_id}/student/{student_id}'
                            response = requests.get(api_url, headers=HEADERS)

                            if response.status_code == 200:
                                relation_data = response.json()
                                self._update_relation_in_odoo(relationship, relation_data)
                            elif response.status_code == 404:
                                # Handle 404: Record has been deleted, unlink the relationship in Odoo
                                relationship.unlink()
                            else:
                                # Handle other non-200 status codes if needed
                                response.raise_for_status()
                        except Exception as e:
                            # Handle request exceptions (e.g., connection errors)
                            return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                    'type': 'danger',
                                    'title': 'Error!',
                                    'message': f"Request failed for student_id={student_id}, parent_id={parent_id}: {e}",
                                    'sticky': False,
                                },
                            }

                    self.get_relations()
                    self.update_user_define_records()
                    self.update_single_dob_gender()
                    self.update_enrollment_histories()
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Record is not updated!',
                            'message': str("Person Student Id is Missing..."),
                            'sticky': False,
                        },
                    }
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Record Updated!',
                    'message': str("Record Updated Successfully..."),
                    'sticky': False,
                },
            }
        else:
            for facts_id in student_ids:
                rec = self.env['res.partner'].search([('is_student', '=', True), ('facts_id', '=', facts_id)])
                if rec.person_student_id:
                    response_student = self.make_request(
                        f'https://api.factsmgt.com/Students/{rec.person_student_id}')
                    student_data = response_student
                    academic_student_data = student_data.get('school')
                    if student_data:
                        if student_data.get('personStudentId', None):
                            if rec.person_student_id != student_data.get('personStudentId'):
                                rec.person_student_id = student_data.get('personStudentId')
                        if student_data.get('studentId', None):
                            if rec.facts_id != student_data.get('studentId'):
                                rec.facts_id = student_data.get('studentId')
                        if student_data.get('schoolCode', None):
                            if rec.current_school != student_data.get('schoolCode'):
                                rec.current_school = student_data.get('schoolCode')
                        if academic_student_data.get('status', None):
                            status_name = academic_student_data.get('status')
                            if status_name:
                                status = self.env['enrollment.status'].search([('name', '=', status_name)], limit=1)
                                if not status:
                                    status = self.env['enrollment.status'].create({'name': status_name})
                                if rec.current_enroll_status != academic_student_data.get('status'):
                                    rec.current_enroll_status = status.id
                        if academic_student_data.get('gradeLevel', None):
                            if rec.current_grade != academic_student_data.get('gradeLevel'):
                                rec.current_grade = academic_student_data.get('gradeLevel')
                        if academic_student_data.get('nextStatus', None):
                            status_name = academic_student_data.get('nextStatus')
                            if status_name:
                                status = self.env['enrollment.status'].search([('name', '=', status_name)], limit=1)
                                if not status:
                                    status = self.env['enrollment.status'].create({'name': status_name})
                                if rec.next_enroll_status != academic_student_data.get('status'):
                                    rec.next_enroll_status = status.id
                        if academic_student_data.get('nextGradeLevel', None):
                            if rec.next_grade != academic_student_data.get('nextGradeLevel'):
                                rec.next_grade = academic_student_data.get('nextGradeLevel')
                    response_general_data = self.make_request(
                        f'https://api.factsmgt.com/People/{rec.facts_id}')
                    student_general_data = response_general_data
                    if student_general_data:
                        if student_general_data.get('firstName', None):
                            if rec.first_name != student_general_data.get('firstName'):
                                rec.first_name = student_general_data.get('firstName')
                        if student_general_data.get('lastName', None):
                            if rec.last_name != student_general_data.get('lastName', None):
                                rec.last_name = student_general_data.get('lastName')
                        if student_general_data.get('email', None):
                            if rec.email != student_general_data.get('email', None):
                                rec.email = student_general_data.get('email', None)
                        if student_general_data.get('email2', None):
                            if rec.email != student_general_data.get('email2', None):
                                rec.email = rec.email + "," + student_general_data.get('email2', None)
                        if student_general_data.get('homePhone', None):
                            if rec.phone != student_general_data.get('homePhone', None):
                                rec.phone = student_general_data.get('homePhone', None)
                        if student_general_data.get('cellPhone', None):
                            if rec.mobile != student_general_data.get('cellPhone', None):
                                rec.mobile = student_general_data.get('cellPhone', None)
                    addressId = student_general_data.get('addressID', None)
                    if addressId != 0 and addressId != None:
                        response_address_data = self.make_request(
                            f'https://api.factsmgt.com/people/Address/{addressId}')
                        address_data = response_address_data
                        if address_data:
                            if address_data.get('address1', None):
                                if rec.street != address_data.get('address1', None):
                                    rec.street = address_data.get('address1')
                            if address_data.get('address2', None):
                                if rec.street2 != address_data.get('address2'):
                                    rec.street2 = address_data.get('address2', None)
                            if address_data.get('city', None):
                                if rec.city != address_data.get('city', None):
                                    rec.city = address_data.get('city', None)
                            if address_data.get('state', None):
                                if rec.state_id.name != address_data.get('state', None):
                                    rec.state_id = self.env['res.country.state'].search(
                                        ['&', ('name', '=', address_data.get('state')), ('country_id', '=', 177)]).id
                            if address_data.get('zip', None):
                                if rec.zip != address_data.get('zip', None):
                                    rec.zip = address_data.get('zip', None)
                    response_homeroom = self.make_request(f'{BASE_URL_HOMEROOM}/{rec.facts_id}')
                    data_homeroom = response_homeroom
                    list_of_data_homeroom = data_homeroom.get('results', [])
                    if list_of_data_homeroom:
                        list_of_data_homeroom = list_of_data_homeroom[-1]
                        new_section = list_of_data_homeroom.get('section', None)
                        existing_string = rec.homeroom
                        if existing_string:
                            old_homeroom = existing_string.split('-')
                            if len(old_homeroom) > 1:
                                old_section = old_homeroom[1]
                                if old_section != new_section:
                                    existing_string = old_homeroom[0]
                                    rec.homeroom = existing_string + '-' + new_section if new_section else existing_string + '-' + old_section
                    student_rec = self.env['res.partner'].search(
                        [('facts_id', '=', facts_id), ('is_student', '=', True)])
                    for relationship in student_rec.student_relationship_ids:
                        parent_id = relationship.parent_id.facts_id
                        student_id = rec.facts_id
                        try:
                            api_url = f'https://api.factsmgt.com/people/ParentStudent/parent/{parent_id}/student/{student_id}'
                            response = requests.get(api_url, headers=HEADERS)

                            if response.status_code == 200:
                                relation_data = response.json()
                                self._update_relation_in_odoo(relationship, relation_data)
                            elif response.status_code == 404:
                                # Handle 404: Record has been deleted, unlink the relationship in Odoo
                                relationship.unlink()
                            else:
                                # Handle other non-200 status codes if needed
                                response.raise_for_status()
                        except Exception as e:
                            # Handle request exceptions (e.g., connection errors)
                            return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                    'type': 'danger',
                                    'title': 'Error!',
                                    'message': f"Request failed for student_id={student_id}, parent_id={parent_id}: {e}",
                                    'sticky': False,
                                },
                            }
                    self.get_relations()
                    self.update_user_define_records()
                    self.update_single_dob_gender()
                    self.update_enrollment_histories()
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Record is not Updated!',
                            'message': str("Person Student Id is Missing..."),
                            'sticky': False,
                        },
                    }
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Record Updated!',
                    'message': str("Record Updated Successfully..."),
                    'sticky': False,
                },
            }

    def update_user_define_records(self):
        user_define_data = self.user_define_data()
        for rec in self:
            user_define_data = self.env['user.define.data'].search([('linked_id', '=', rec.facts_id)]).mapped('data')
            print(user_define_data)
            # Create a list of dictionaries to be passed to create() method
            concession_data = []
            if user_define_data:
                if user_define_data[0] == '':
                    user_define_data[0] = user_define_data[1]
                    user_define_data[1] = user_define_data[2]
                    user_define_data[2] = user_define_data[3]
                # Append each data set as a dictionary to the concession_data list
                concession_data.append({
                    'concession_type': user_define_data[0],
                    'discount_percentage': user_define_data[1],
                    'concession_reason': user_define_data[2]
                })
                # Write the concession_data to the One2many field
                if len(rec.student_concessions) < 1:
                    rec.student_concessions = [(0, 0, line_data) for line_data in concession_data]

                elif len(rec.student_concessions) >= 1:
                    if user_define_data[0] and user_define_data[1] and user_define_data[2]:
                        for concession_record in rec.student_concessions:
                            if (concession_record.concession_type != user_define_data[0].lower() or
                                    concession_record.discount_percentage != user_define_data[1] or
                                    concession_record.concession_reason != user_define_data[2]):
                                concession_record.write({
                                    'concession_type': user_define_data[0].lower(),
                                    'discount_percentage': user_define_data[1],
                                    'concession_reason': user_define_data[2]
                                })

    def user_define_data(self):
        try:
            BASE_URL = BASE_URL_USERDEFINEDDATA
            response_user_define_data = requests.get(BASE_URL, headers=HEADERS)
            if response_user_define_data.status_code == 200:
                response_user_define_data.raise_for_status()
                data_students = response_user_define_data.json()
                all_students = []
                max_pages = data_students.get('pageCount')  # Maximum number of pages to fetch
                page = 1
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'danger',
                        'title': 'Error!',
                        'message': f"Not Responding from server status code is {response_user_define_data.status_code}",
                        'sticky': False,
                    },
                }
            while BASE_URL and page <= max_pages:
                response_user_define_data = self.make_request(BASE_URL)
                data_students = response_user_define_data
                list_of_user_define_data = data_students.get('results', [])
                user_define_obj = self.env['user.define.data']
                for user_define_data in list_of_user_define_data:
                    student_id = user_define_data.get('linkedId')
                    id = user_define_data.get('id')
                    existing_record = self.env['user.define.data'].search(
                        [('linked_id', '=', student_id), ('data_id', '=', id)])
                    student = self.env['res.partner'].search([('facts_id', '=', student_id), ('is_student', '=', True)])
                    if student:
                        if not existing_record:
                            user_define_obj.create({
                                'id': user_define_data.get('id'),
                                'data_id': user_define_data.get('dataId'),
                                'field_id': user_define_data.get('fieldId'),
                                'linked_id': user_define_data.get('linkedId'),
                                'data': user_define_data.get('data')
                            })
                        else:
                            existing_record.update({
                                'data_id': user_define_data.get('dataId'),
                                'field_id': user_define_data.get('fieldId'),
                                'linked_id': user_define_data.get('linkedId'),
                                'data': user_define_data.get('data')
                            })
                BASE_URL = data_students.get('nextPage')  # Get the next page URL
                page += 1
            return

        except Exception as e:
            _logger.exception('Error while fetching and creating individuals: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Error!',
                    'message': str(e),
                    'sticky': False,
                },
            }

    def button_update_relationships(self):
        try:
            get_all_families = self.env['res.partner'].search([('is_company', '=', 'True')])
            for family in get_all_families:
                get_person_family = self.env['person.family'].search([('family_id', '=', family.id)])
                get_parents = get_person_family.person_id.search(
                    [('facts_id', 'in', get_person_family.person_id.mapped('facts_id')), ('is_parent', '=', True)])
                get_students = get_person_family.person_id.search(
                    [('facts_id', 'in', get_person_family.person_id.mapped('facts_id')), ('is_student', '=', True)])
                family.write({'family_parent_ids': [(6, 0, get_parents.ids)]})
                family.write({'family_student_ids': [(6, 0, get_students.ids)]})
        except Exception as e:
            _logger.exception('Error while fetching and creating individuals: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Error!',
                    'message': str(e),
                    'sticky': False,
                },
            }

    def write(self, vals):
        res = super(StudentManager, self).write(vals)
        if 'current_enroll_status' in vals or 'current_grade_selection' in vals:
            self.create_enrollment_history(self)
        for partner in self:
            enroll_status_id = vals.get('current_enroll_status')
            if enroll_status_id:
                enroll_status = self.env['enrollment.status'].browse(enroll_status_id)
                if enroll_status.name != 'Registration':
                    if not partner.student_code:
                        branch = partner.branch_id
                        if branch:
                            branch_code = branch.branch_code
                            set_student_code = branch.set_student_code

                            # Get the last student code for the branch
                            last_student = self.search([
                                ('branch_id', '=', branch.id),
                                ('is_student', '=', True),
                                ('student_code', '!=', False)
                            ], order='student_code desc', limit=1)

                            if last_student and last_student.student_code:
                                last_student_code = int(last_student.student_code[len(branch_code):])
                            else:
                                last_student_code = set_student_code

                            new_student_code = last_student_code + 1
                            partner.student_code = f"{branch_code}{new_student_code:04d}"

            if enroll_status_id:
                if enroll_status.name.strip().lower() == 'withdrawn' or enroll_status.name.strip().lower() == 'graduate':
                    existing_subscription = self.env['sale.subscription'].search([
                        ('partner_id', '=', partner.id),
                    ])
                    closed_stage_id = self._get_closed_stage_id()

                    if closed_stage_id and existing_subscription:
                        existing_subscription.write({'stage_id': closed_stage_id})
        return res

    def create_enrollment_history(self, student):
        self.env['enrollment.histories'].create({
            'status': student.current_enroll_status.name,
            'grade_level': student.current_grade_selection,
            'school_name': student.branch_id.name,
            'enrollment_history_id': student.id,
        })
        return

    def populate_student_ids_in_relationships(self):
        # Loop through all student records
        student_ids = self.env['relationship.info'].search([]).mapped('student_id.id')
        students = self.env['res.partner'].search([('title', '=', 'Student')])
        for student in students:
            if student.id in student_ids:
                relationship_info = self.env['relationship.info'].search([
                    ('student_id', '=', student.id),
                    # Add any other conditions to filter the correct relationship record
                ])
                student.write({'student_relationship_ids': [(6, 0, relationship_info.ids)]})
        # Commit the changes to the database
        self.env.cr.commit()

    def assign_titles(self):
        all_students = self.env['res.partner'].search([('is_student', '=', True)])
        for student in all_students:
            student.title = self.env['res.partner.title'].search([('name', '=', 'Student')]).id

    @api.model
    def get_students(self):
        country_code = ""
        baseURL = 'https://api.factsmgt.com/Students'
        pageSize = self.make_request(BASE_URL_STUDENTS)
        get_total_students = pageSize['rowCount']
        params = urllib.parse.urlencode({
            'PageSize': f'{get_total_students}',
        })
        base_student_url = f"{baseURL}?{params}"
        data_students = self.make_request(base_student_url)
        counter = 0
        no_existing_student = 0
        try:
            all_students = []
            list_of_students = data_students.get('results', [])
            student_obj = self.env['res.partner']
            for student_data in list_of_students:
                student_id = student_data.get('studentId')
                list_of_students_academic_info = student_data['school']
                if not student_id:
                    _logger.warning('Student ID is missing in data: %s', student_data)
                    continue
                # Check if a student with the same student_id already exists
                existing_student = student_obj.search([('facts_id', '=', student_id)])
                no_existing_student += 1
                print("existing students are", no_existing_student)
                if not existing_student:
                    # Fetch data from the People API using the person_id
                    person_id = student_data.get('studentId')
                    if person_id:
                        list_of_students_academic_info = student_data.get('school', {})
                        response_people = self.make_request(f'{BASE_URL_PEOPLE}/{person_id}')
                        data_people = response_people
                        # Create a new student record
                        status_name = list_of_students_academic_info.get('status', None)
                        current_status = ""
                        if status_name:
                            current_status = self.env['enrollment.status'].search([('name', '=', status_name)], limit=1)
                            if not current_status:
                                current_status = self.env['enrollment.status'].create({'name': status_name})
                        next_status = list_of_students_academic_info.get('nextStatus')
                        if status_name:
                            next_status = self.env['enrollment.status'].search([('name', '=', status_name)], limit=1)
                            if not next_status:
                                next_status = self.env['enrollment.status'].create({'name': status_name})
                        student = student_obj.sudo().create({
                            'person_student_id': student_data.get('personStudentId'),
                            'is_student': True,
                            'is_parent': False,
                            'facts_id': student_id,
                            'branch_id': self.env['res.branch'].search(
                                [('id', 'in', self._context.get('allowed_branch_ids'))]).id,
                            'name': data_people.get('firstName', None),
                            'first_name': data_people.get('firstName', None),
                            'last_name': data_people.get('lastName', None),
                            'phone': data_people.get('homePhone', None),
                            'mobile': data_people.get('cellPhone', None),
                            'email': data_people.get('email', None),
                            'title': self.env['res.partner.title'].search([('name', '=', 'Student')]).id,
                            'current_grade': list_of_students_academic_info.get('gradeLevel',
                                                                                None) if list_of_students_academic_info.get(
                                'gradeLevel', None) else "None",
                            'next_grade': list_of_students_academic_info.get('nextGradeLevel',
                                                                             None) if list_of_students_academic_info.get(
                                'nextGradeLevel', None) else "None",
                            'current_enroll_status': current_status.id,
                            'next_enroll_status': next_status.id,
                            'homeroom': list_of_students_academic_info.get('gradeLevel',
                                                                           None) if list_of_students_academic_info.get(
                                'gradeLevel', None) else "None",
                            'current_school': student_data.get('schoolCode', None) if student_data.get(
                                'schoolCode', None) else "None",
                            'next_school': list_of_students_academic_info.get('nextSchoolCode',
                                                                              None) if list_of_students_academic_info.get(
                                'schoolCode', None) else "None",
                            # Add other student fields here
                        })
                        # Fetch address data from the Address API using addressID
                        address_id = data_people.get('addressID')
                        if address_id:
                            response_address = self.make_request(f'{BASE_URL_ADDRESS}/{address_id}')
                            data_address = response_address
                            if data_address.get('country') == "PAK" or data_address.get(
                                    'country') == "Pakistan":
                                country_code = "PK"
                            if not data_address.get('country', None):
                                country_code = "PK"
                            get_country_id = self.env['res.country'].search([('code', '=', country_code)]).id
                            # Update the student's address information
                            student.sudo().write({
                                'street': f"{data_address.get('address1')} {data_address.get('address2')}",
                                'city': data_address.get('city'),
                                # 'state': data_address.get('state'),
                                'zip': data_address.get('zip'),
                                'country_id': get_country_id,
                            })
                        counter += 1
                        print(counter, "Student record is created")
                        all_students.append(student.id)
                else:
                    person_id = student_data.get('studentId')
                    if not existing_student.street and existing_student.city and existing_student.country_id and existing_student.zip:
                        if person_id:
                            response_people = self.make_request(f'{BASE_URL_PEOPLE}/{person_id}')
                            data_people = response_people
                            address_id = data_people.get('addressID')
                            if address_id:
                                response_address = self.make_request(f'{BASE_URL_ADDRESS}/{address_id}')
                                data_address = response_address
                                if data_address.get('country') == "PAK" or data_address.get(
                                        'country') == "Pakistan":
                                    country_code = "PK"
                                if not data_address.get('country', None):
                                    country_code = "PK"
                                get_country_id = self.env['res.country'].search([('code', '=', country_code)]).id
                                # Update the existing student's address information
                                existing_student.sudo().write({
                                    'street': f"{data_address.get('address1')} {data_address.get('address2')}",
                                    'city': data_address.get('city', None),
                                    # 'state': data_address.get('state'),
                                    'zip': data_address.get('zip', None),
                                    'country_id': get_country_id,
                                })
                            all_students.append(existing_student.id)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Success!',
                    'message': f'{len(all_students)} individuals fetched.',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.exception('Error while fetching and creating individuals: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Error!',
                    'message': str(e),
                    'sticky': False,
                },
            }

    def update_homeroom_for_existing_records(self):
        get_all_students = self.env['res.partner'].search([('is_student', '=', True)])
        for student in get_all_students:
            pattern = r'-[A-Za-z]+'
            if student.facts_id and student.homeroom != "None":
                if not re.search(pattern, student.homeroom):
                    student_id = student.facts_id
                    # Make API request to get homeroom information
                    response_homeroom = self.make_request(f'{BASE_URL_HOMEROOM}/{student_id}')
                    data_homeroom = response_homeroom
                    list_of_data_homeroom = data_homeroom.get('results', [])
                    if list_of_data_homeroom:
                        list_of_data_homeroom = list_of_data_homeroom[-1]
                        section = list_of_data_homeroom.get('section', None)
                        existing_string = student.homeroom
                        student.homeroom = existing_string + '-' + section if student.homeroom else "None"
                        student.is_student = True

    # @api.depends('facts_id')
    # def _compute_homeroom(self):
    #     for student in self:
    #         student_id = student.facts_id
    #
    #         # Make API request to get homeroom information
    #         response_homeroom = requests.get(f'{BASE_URL_HOMEROOM}/{student_id}',headers=HEADERS)
    #         response_homeroom.raise_for_status()
    #         data_homeroom = response_homeroom.json()
    #
    #         # Update homeroom field in the student record
    #         student.homeroom = data_homeroom.get('section', '')

    @api.model
    def get_families_details(self):
        try:
            baseURL = BASE_URL_FAMILIES
            pageSize = self.make_request(BASE_URL_FAMILIES)
            get_total_families = pageSize['rowCount']
            params = urllib.parse.urlencode({
                'PageSize': f'{get_total_families}',
            })
            base_families_url = f"{baseURL}?{params}"
            data_families = self.make_request(base_families_url)
            all_families = []
            list_of_families = data_families['results']
            family_obj = self.env['res.partner']
            counter = 0
            for family_data in list_of_families:
                family_id = family_data.get('familyID', None)
                # Check if a family with the same family_id already exists
                existing_family = family_obj.search([('facts_id', '=', family_id)])
                counter += 1
                print("total number of families", counter)
                if not existing_family:
                    # Create a new record in school.family.individual for the student
                    family = family_obj.create({
                        'company_type': "company",
                        'facts_id': family_data.get('familyID'),
                        'name': family_data.get('familyName'),
                        'is_company': True,
                        # Add other individual fields here
                    })
                    all_families.append(family.id)
                else:
                    existing_family.write({
                        'is_company': True,
                        'company_type': "company",
                    })
                    all_families.append(existing_family.id)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Success!',
                    'message': f'{len(all_families)} individuals fetched.',
                    'sticky': False,
                }
            }
        except Exception as e:
            # Handle any exceptions here
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Error!',
                    'message': str(e),
                    'sticky': False,
                },
            }

    @api.model
    def get_individuals(self):
        baseURL = BASE_URL_PEOPLE
        pageSize = self.make_request(BASE_URL_PEOPLE)
        get_total_individuals = pageSize['rowCount']
        params = urllib.parse.urlencode({
            'PageSize': f'{get_total_individuals}',
        })
        base_url_people = f"{baseURL}?{params}"
        data_parents = self.make_request(base_url_people)
        all_individuals = []
        try:
            list_of_parents = data_parents['results']
            individual_obj = self.env['res.partner']
            counter = 0
            for parent_data in list_of_parents:
                parent_id = parent_data['personId']
                # Check if a person with the same student_id already exists
                is_student = self.env['res.partner'].search(
                    [('facts_id', '=', parent_id), ('is_student', '=', True)])
                existing_parent = individual_obj.search([('facts_id', '=', parent_id)])
                if not is_student:
                    counter += 1
                    print("Total number of parents", counter)
                    if not existing_parent:
                        # Fetch data from the People API using the person_id
                        response_people = self.make_request(f'{BASE_URL_PEOPLE}/{parent_id}')
                        data_people = response_people
                        # Fetch address data using addressId
                        try:
                            if parent_data.get('addressID', None):
                                address_id = parent_data.get('addressID')
                                response_address = self.make_request(f'{BASE_URL_ADDRESS}/{address_id}')
                                data_address = response_address
                                # Map address data to Odoo fields
                                street = data_address.get('address1', None)
                                state_id = data_address.get('state', None)
                                city = data_address.get('city', None)
                                if data_address.get('country') == "PAK" or data_address.get(
                                        'country') == "Pakistan":
                                    country_code = "PK"
                                    get_country_id = self.env['res.country'].search(
                                        [('code', '=', country_code)]).id
                                else:
                                    country_code = get_country_id = self.env['res.country'].search(
                                        [('code', '=', 'PK')]).id
                            else:
                                street = "None"
                                state_id = "None"
                                city = "None"
                                get_country_id = self.env['res.country'].search([('code', '=', "PK")]).id
                        except Exception as e:
                            return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                    'type': 'danger',
                                    'title': 'Error!',
                                    'message': str(e),
                                    'sticky': False,
                                },
                            }
                        # Create a new record in school.family.individual for the parent
                        name = data_people['firstName'] + " " + data_people['lastName']
                        individual = individual_obj.create({
                            'facts_id': data_people['personId'],
                            'person_student_id': data_people['personId'],
                            'is_student': False,
                            'is_parent': True,
                            'branch_id': self.env['res.branch'].search(
                                [('id', 'in', self._context.get('allowed_branch_ids'))]).id,
                            'name': name,
                            'title': self.env['res.partner.title'].search([('name', '=', 'Parent')]).id,
                            'first_name': data_people.get('firstName', None),
                            'last_name': data_people.get('lastName', None),
                            'email': data_people.get('email', None),
                            'phone': data_people.get('cellPhone', None),
                            'street': street,
                            # 'state_id': self.env['res.country.state'].search([('code', '=', state_id)]).id,
                            'city': city,
                            'country_id': get_country_id

                            # Add other individual fields here
                        })
                        all_individuals.append(individual.id)
                    else:
                        person_id = parent_data.get('personId')
                        if not existing_parent.street and existing_parent.city and existing_parent.zip and existing_parent.country_id:
                            if person_id:
                                response_people = self.make_request(f'{BASE_URL_PEOPLE}/{person_id}')
                                data_people = response_people
                                address_id = data_people.get('addressID')
                                if address_id:
                                    response_address = self.make_request(f'{BASE_URL_ADDRESS}/{address_id}')
                                    data_address = response_address
                                    if data_address.get('country') == "PAK" or data_address.get(
                                            'country') == "Pakistan":
                                        country_code = "PK"
                                        get_country_id = self.env['res.country'].search(
                                            [('code', '=', country_code)]).id
                                    else:
                                        country_code = get_country_id = self.env['res.country'].search(
                                            [('code', '=', 'PK')]).id
                                    # Update the existing student's address information
                                    existing_parent.write({
                                        'street': f"{data_address.get('address1')} {data_address.get('address2')}",
                                        'city': data_address.get('city'),
                                        # 'state': data_address.get('state'),
                                        'zip': data_address.get('zip'),
                                        'country_id': get_country_id,
                                    })

                                all_individuals.append(existing_parent.id)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Success!',
                    'message': f'{len(all_individuals)} individuals fetched.',
                    'sticky': False,
                }
            }
        except Exception as e:
            # Handle any exceptions here
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Error!',
                    'message': str(e),
                    'sticky': False,
                },
            }

    @api.model
    def get_relations(self):
        # Call the method from the related model
        relationship_model = self.env['relationship.info']
        relationship_model.get_relations()

    @api.model
    def get_person_family(self):
        # Call the method from the related model
        relationship_model = self.env['person.family']
        relationship_model.get_person_family()

    @api.model
    def get_enrollment_history(self):
        try:
            BASE_URL = BASE_URL_ENROLLMENT
            response_enrollment_history = requests.get(BASE_URL, headers=HEADERS)
            if response_enrollment_history.status_code == 200:
                response_enrollment_history.raise_for_status()
                data_enrollment_history = response_enrollment_history.json()
                all_enrollment_histories = []
                max_pages = data_enrollment_history.get('pageCount')  # Maximum number of pages to fetch
                page = 1
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'danger',
                        'title': 'Error!',
                        'message': f"Not Responding from server status code is {response_enrollment_history.status_code}",
                        'sticky': False,
                    },
                }
            while BASE_URL and page <= max_pages:
                response_enrollment_history = self.make_request(BASE_URL)
                data_enrollment_history = response_enrollment_history
                list_enrollment_history = data_enrollment_history['results']
                enrollment_history = self.env['enrollment.histories']
                for enrollment_data in list_enrollment_history:
                    student_id = enrollment_data.get('studentId', None)
                    existing_student_history = enrollment_history.search(
                        [('history_id', '=', enrollment_data.get('enrollmentHistoryId'))])
                    existing_student = self.env['res.partner'].search([('facts_id', '=', student_id)])
                    if not existing_student_history:
                        if student_id:
                            enrollment_history.create({
                                'history_id': enrollment_data.get('enrollmentHistoryId', None),
                                'enrollment_history_id': existing_student.id,
                                'date': enrollment_data.get('beginDate', None),
                                'grade_level': enrollment_data.get('gradeLevel', None),
                                'notes': enrollment_data.get('note', None),
                                'status': enrollment_data.get('status', None),
                                'school_name': enrollment_data.get('schoolCode', None),
                            })
                            all_enrollment_histories.append(enrollment_history.id)
                BASE_URL = data_enrollment_history.get('nextPage')  # Get the next page URL
                page += 1

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Success!',
                    'message': f'{len(all_enrollment_histories)} enrollment histories fetched from {page - 1} pages.',
                    'sticky': False,
                }
            }
        except Exception as e:
            # Handle any exceptions here
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Error!',
                    'message': str(e),
                    'sticky': False,
                },
            }

    def update_enrollment_history(self):
        all_students = self.env['res.partner'].search([('is_student', '=', True)])
        for student in all_students:
            student_id = student.id
            enrollment_histories = self.env['enrollment.histories'].search([('enrollment_history_id', '=', student_id)])
            student.write({'enrollment_histories_ids': [(6, 0, enrollment_histories.ids)]})
