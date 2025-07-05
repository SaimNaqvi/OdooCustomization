# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, modules, fields, _
import urllib.request
import urllib.parse
import json
import logging
import requests
import re
import ast
from PIL import Image
import io
from datetime import datetime
from retry import retry
from requests.exceptions import HTTPError, ConnectionError
from collections import defaultdict

file_path = 'custom_addons/student_manager/models/images.txt'
_logger = logging.getLogger(__name__)

BASE_URL_STUDENTS = 'https://api.factsmgt.com/Students'
BASE_URL_PEOPLE = 'https://api.factsmgt.com/People'
BASE_URL_ADDRESS = 'https://api.factsmgt.com/people/Address'
BASE_URL_HOMEROOM = 'https://api.factsmgt.com/Classes/students'
# BASE_URL_PEOPLE = 'https://api.factsmgt.com/People'
BASE_URL_FAMILIES = 'https://api.factsmgt.com/families'
BASE_URL_RELATION = 'https://api.factsmgt.com/people/ParentStudent'
BASE_URL_ENROLLMENT = 'https://api.factsmgt.com/students/EnrollmentHistories'
BASE_URL_USERDEFINEDDATA = 'https://api.factsmgt.com/UserDefinedData'
HEADERS = {
    'Ocp-Apim-Subscription-Key': '03f001e670f14071acb128360118bf97',
    'Facts-Api-Key': '0UP1qsO4hH3U6QQKvK7KWszA631/e6YcVTNBC2QP46qIQg7NVgDYoXYqbuuj35lfSALndtkKJwWnqrH9r6xKHaKqjmpDK3XdmkGvHE1P1Xg=',
}


class UpdateParentRecords(models.Model):
    _inherit = 'res.partner'
    user_name = fields.Char(string='User Name', store=True)

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

    def _update_relation_in_odoo(self, relationship, relation_data):
        # Use the relation_data to update records in Odoo
        relationship.write({
            'relationship_type': relation_data.get('relationship'),
            'custody': relation_data.get('custody'),
            'correspondence': relation_data.get('correspondence'),
            # Add other fields as needed...
        })

    def update_all_parent_record(self, all_parents):
        for rec in all_parents:
            if rec.facts_id:
                response_parent = self.make_request(f'https://api.factsmgt.com/People/{rec.facts_id}')
                person_data = response_parent
                if person_data:
                    if person_data.get('firstName', None):
                        if rec.first_name != person_data.get('firstName'):
                            rec.current_school = person_data.get('firstName')
                    if person_data.get('lastName', None):
                        if rec.last_name != person_data.get('lastName'):
                            rec.last_name = person_data.get('lastName')
                    if person_data.get('email', None):
                        if rec.email != person_data.get('email'):
                            rec.email = person_data.get('email')
                    if person_data.get('email2', None):
                        if rec.email != person_data.get('email2'):
                            rec.email = rec.email + "," + person_data.get('email2', None)
                    if person_data.get('username', None):
                        if rec.user_name != person_data.get('username'):
                            rec.user_name = person_data.get('username')
                    if person_data.get('homePhone', None):
                        if rec.phone != person_data.get('homePhone', None):
                            rec.phone = person_data.get('homePhone', None)
                    if person_data.get('cellPhone', None):
                        if rec.mobile != person_data.get('cellPhone', None):
                            rec.mobile = person_data.get('cellPhone', None)
                addressId = person_data.get('addressID', None)
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
                        if address_data.get('state', None):
                            if rec.state_id.name != address_data.get('state', None):
                                rec.state_id = self.env['res.country.state'].search(['&', ('name', '=', address_data.get('state')), ('country_id', '=', 177)]).id
                                if not rec.state_id:
                                    new_state = self.env['res.country.state'].create({
                                        'name': 'Sindh',
                                        'country_id': self.env['res.country'].search(
                                            [('name', '=', address_data.get('country', None))]).id,
                                        'code': 'PK-SD'})
                                    rec.state_id = new_state.id if new_state else None
                        if address_data.get('zip', None):
                            if rec.zip != address_data.get('zip', None):
                                rec.zip = address_data.get('zip', None)
                for relationship in rec.student_ids:
                    student_id = relationship.student_id.facts_id
                    parent_id = rec.facts_id
                    try:
                        api_url = f'https://api.factsmgt.com/people/ParentStudent/parent/{parent_id}/student/{student_id}'
                        relation_data = self.make_request(api_url)

                        if relation_data is not None:
                            self._update_relation_in_odoo(relationship, relation_data)
                        else:
                            # Handle 404: Record has been deleted, unlink the relationship in Odoo
                            relationship.unlink()
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
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'error',
                        'title': 'Record Updated!',
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

    def dob_gender_update(self):
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

    def update_parent_record(self, parent_ids=None):
        if parent_ids is None:
            for rec in self:
                if rec.facts_id:
                    response_parent = self.make_request(f'https://api.factsmgt.com/People/{rec.facts_id}')
                    person_data = response_parent
                    if person_data:
                        if person_data.get('firstName', None):
                            if rec.first_name != person_data.get('firstName'):
                                rec.current_school = person_data.get('firstName')
                        if person_data.get('lastName', None):
                            if rec.last_name != person_data.get('lastName'):
                                rec.last_name = person_data.get('lastName')
                        if person_data.get('email', None):
                            if rec.email != person_data.get('email'):
                                rec.email = person_data.get('email')
                        if person_data.get('email2', None):
                            if rec.email != person_data.get('email2'):
                                rec.email = rec.email + "," + person_data.get('email2', None)
                        if person_data.get('username', None):
                            if rec.user_name != person_data.get('username'):
                                rec.user_name = person_data.get('username')
                        if person_data.get('homePhone', None):
                            if rec.phone != person_data.get('homePhone', None):
                                rec.phone = person_data.get('homePhone', None)
                        if person_data.get('cellPhone', None):
                            if rec.mobile != person_data.get('cellPhone', None):
                                rec.mobile = person_data.get('cellPhone', None)

                    addressId = person_data.get('addressID', None)
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
                    for relationship in rec.student_ids:
                        student_id = relationship.student_id.facts_id
                        parent_id = rec.facts_id
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
                    self.get_relations()
                    self.update_cnic()
                    self.dob_gender_update()
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'error',
                            'title': 'Record Updated!',
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
            for facts_id in parent_ids:
                rec = self.env['res.partner'].search([('is_parent', '=', True), ('facts_id', '=', facts_id)])
                if rec.facts_id:
                    response_parent = self.make_request(
                        f'https://api.factsmgt.com/People/{rec.facts_id}')
                    person_data = response_parent
                    if person_data:
                        if person_data.get('firstName', None):
                            if rec.first_name != person_data.get('firstName'):
                                rec.current_school = person_data.get('firstName')
                        if person_data.get('lastName', None):
                            if rec.last_name != person_data.get('lastName'):
                                rec.last_name = person_data.get('lastName')
                        if person_data.get('email', None):
                            if rec.email != person_data.get('email'):
                                rec.email = person_data.get('email')
                        if person_data.get('email2', None):
                            if rec.email != person_data.get('email2'):
                                rec.email = rec.email + "," + person_data.get('email2', None)
                        if person_data.get('username', None):
                            if rec.user_name != person_data.get('username'):
                                rec.user_name = person_data.get('username')
                        if person_data.get('homePhone', None):
                            if rec.phone != person_data.get('homePhone', None):
                                rec.phone = person_data.get('homePhone', None)
                        if person_data.get('cellPhone', None):
                            if rec.mobile != person_data.get('cellPhone', None):
                                rec.mobile = person_data.get('cellPhone', None)

                    addressId = person_data.get('addressID', None)
                    if addressId != 0 and addressId is not None:
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
                    for relationship in rec.student_ids:
                        student_id = relationship.student_id.facts_id
                        parent_id = rec.facts_id
                        try:
                            api_url = f'https://api.factsmgt.com/people/ParentStudent/parent/{parent_id}/student/{student_id}'
                            relation_data = self.make_request(api_url)
                            if relation_data is not None:
                                self._update_relation_in_odoo(relationship, relation_data)
                            else:
                                # Handle 404: Record has been deleted, unlink the relationship in Odoo
                                relationship.unlink()
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
                    self.update_cnic()
                    self.dob_gender_update()
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'error',
                            'title': 'Record Updated!',
                            'message': str("Person facts Id is Missing..."),
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

    @api.model
    def get_relations(self):
        # Call the method from the related model
        relationship_model = self.env['relationship.info']
        relationship_model.get_relations()
