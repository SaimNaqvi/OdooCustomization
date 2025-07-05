# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, modules, fields, _
import urllib.request
import urllib.parse
import json
import logging
from retry import retry
import requests
from requests.exceptions import HTTPError, ConnectionError

BASE_URL_RELATION = 'https://api.factsmgt.com/people/ParentStudent'
BASE_URL_PEOPLE = 'https://api.factsmgt.com/People'
BASE_URL_ADDRESS = 'https://api.factsmgt.com/people/Address'

HEADERS = {
    'Ocp-Apim-Subscription-Key': '03f001e670f14071acb128360118bf97',
    'Facts-Api-Key': '0UP1qsO4hH3U6QQKvK7KWszA631/e6YcVTNBC2QP46qIQg7NVgDYoXYqbuuj35lfSALndtkKJwWnqrH9r6xKHaKqjmpDK3XdmkGvHE1P1Xg=',
}
relationship_types = [
    ('aunt', 'Aunt'),
    ('brother', 'Brother'),
    ('donor', 'Donor'),
    ('father', 'Father'),
    ('friend', 'Friend'),
    ('grand parent', 'Grand parent'),
    ('guardian', 'Guardian'),
    ('mother', 'Mother'),
    ('sister', 'Sister'),
    ('spouse', 'Spouse'),
    ('step father', 'Step father'),
    ('step mother', 'Step mother'),
    ('uncle', 'Uncle'),
    ('other', 'Other'),
]

class StudentRelation(models.Model):
    _name = "relationship.info"
    _description = "Student relationship"
    _order = 'student_id'
    student_id = fields.Many2one("res.partner", string="Student", required=True, ondelete="cascade")
    parent_id = fields.Many2one("res.partner", string="Parent", required=True, ondelete="cascade", domain="[('is_parent', '=', True)]")
    parent_name = fields.Char(string="Parent Name")
    relationship_type = fields.Selection(relationship_types, string="RelationShip Type", store=True)

    custody = fields.Boolean(string="Custody")
    is_emergency_contact = fields.Boolean(string="Emergency Contact")
    correspondence = fields.Boolean(string="Correspondence")
    grade_related = fields.Boolean(string="Grade Related")
    family_portal = fields.Boolean(string="Family Portal")
    grandparent = fields.Boolean(string="grandparent")
    reportCard = fields.Boolean(string="reportCard")
    parentsWeb = fields.Boolean(string="parentsWeb")
    # student_parent_ids = [11518, 11519, 11517, 11520, 11522, ]

    # Add a related field to fetch 'facts_id' from the related model
    student_facts_id = fields.Integer(related="student_id.facts_id", string="Student Facts ID", store=True,
                                      readonly=True)
    student_code = fields.Char(related="student_id.student_code", string="Student Facts ID", store=True)

    @api.onchange('student_id')
    def _onchange_student_id(self):
        if self.student_id:
            self.student_facts_id = self.student_id.facts_id
        else:
            self.student_facts_id = False

    def open_student(self):
        self.ensure_one()
        return {
            'name': _("Student"),
            'type': 'ir.actions.act_window',
            'res_model': 'relationship.info',
            'view_mode': 'form',
            'view_id': self.env.ref('student_manager.view_school_student_relationship_form').id,
            'res_id': self.id,
            'target': 'new',
        }

    def name_get(self):
        result = []
        for record in self:
            name = "%s" % (record.student_id.name)  # Customize this format as needed
            result.append((record.id, name))
        return result

    @retry(ConnectionError, delay=2, backoff=2, max_delay=10, tries=3)
    def make_request(self, url):
        try:
            response = requests.get(url, headers=HEADERS)
            # Custom handling based on status code or response content
            if response.status_code == 200:
                return response.json()  # Return JSON data for successful response
            elif response.status_code == 404:
                return None  # Return None for 404 responses
            else:
                # Handle other non-200 status codes if needed
                # You can customize this part based on your requirements
                raise HTTPError(f"Unexpected status code: {response.status_code}")

        except ConnectionError as e:
            raise ConnectionError(f"Connection error: {e}")

        except HTTPError as e:
            # Handle HTTP errors here
            raise HTTPError(f"HTTP error: {e}")

        except Exception as e:
            # Handle other unexpected exceptions
            raise Exception(f"An unexpected error occurred: {e}")

    def create_new_parent(self, parent_id):
        response_people = self.make_request(f'{BASE_URL_PEOPLE}/{parent_id}')
        data_people = response_people
        individual_obj = self.env['res.partner']
        all_individuals = []
        # Fetch address data using addressId
        try:
            if data_people.get('addressID', None):
                address_id = data_people.get('addressID')
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
                    get_country_id = self.env['res.country'].search(
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
            # 'person_student_id': data_people['personId'],
            'is_student': False,
            'is_parent': True,
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
        return individual

    @api.model
    def get_relations(self):
        baseURL = BASE_URL_RELATION
        pageSize = self.make_request(BASE_URL_RELATION)
        get_total_relations = pageSize['rowCount']
        params = urllib.parse.urlencode({
            'PageSize': f'{get_total_relations}',
        })
        base_student_url = f"{baseURL}?{params}"
        data_relations = self.make_request(base_student_url)
        all_realtions = []
        counter=0
        try:
            list_of_relations = data_relations['results']
            for record in list_of_relations:
                parent_id = record.get('parentID')
                student_id = record.get('studentID')
                # # Find the corresponding parent and student records
                parent_partner = self.env['res.partner'].search(
                    [('facts_id', '=', parent_id), ('is_parent', '=', True)],limit=1)
                # create parent if not exists
                if not parent_partner:
                    parent_partner = self.create_new_parent(parent_id)
                student_partner = self.env['res.partner'].search(
                    [('facts_id', '=', student_id), ('is_student', '=', True)])
                if student_partner and parent_partner:
                    relationship_info = self.env['relationship.info'].search([
                        ('parent_id.facts_id', '=', parent_id),  # this should be a multiple
                        ('student_id.facts_id', '=', student_id),  # this should be a unique
                    ])
                    if not relationship_info:
                        relation_ship = relationship_info.create({
                            'parent_id': parent_partner.id,
                            'student_id': student_partner.id,
                            'parent_name': parent_partner.first_name + "" + parent_partner.last_name,
                            'custody': record.get('custody'),
                            'relationship_type': record.get('relationship').lower() if record.get('relationship') else None,
                            'correspondence': record.get('correspondence'),
                            'grandparent': record.get('grandparent'),
                            'reportCard': record.get('reportCard'),
                            'parentsWeb': record.get('parentsWeb'),
                        })
                        counter += 1
                        print(counter, "Relationship created")
                        all_realtions.append(relation_ship.id)
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'type': 'success',
            #         'title': 'Success!',
            #         'message': f'{len(all_realtions)} student relations fetched from {page - 1} pages.',
            #         'sticky': False,
            #     }
            # }
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
    def remove_duplicates(self):
        # Identify duplicate records based on the 'name' field
        duplicates = self.env['relationship.info'].search([],
                                                          order='parent_id')  # You can add other search criteria if needed

        # Keep one instance of each unique record and delete the duplicates
        unique_records = {}
        duplicate_counter = 0
        for duplicate in duplicates:
            # Use the 'name' field as the criteria for uniqueness
            if duplicate.parent_id.name not in unique_records:
                unique_records[duplicate.parent_id.name] = duplicate
            else:
                # Delete duplicate records
                duplicate.unlink()
                duplicate_counter += 1
        if duplicate_counter > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Success!',
                    'message': f'{duplicate_counter} duplictaes unlink from relationship ids field.',
                    'sticky': False,
                }
            }
        # You may want to commit the changes to the database
        self.env.cr.commit()
