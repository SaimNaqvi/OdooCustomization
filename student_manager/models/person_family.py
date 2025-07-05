from odoo import api, models, modules, fields
import urllib.request
import urllib.parse
import json
from retry import retry
from requests.exceptions import HTTPError, ConnectionError
import logging
import requests

BASE_URL_PERSON_FAMILY = 'https://api.factsmgt.com/people/PersonFamily/'
HEADERS = {
    'Ocp-Apim-Subscription-Key': '03f001e670f14071acb128360118bf97',
    'Facts-Api-Key': '0UP1qsO4hH3U6QQKvK7KWszA631/e6YcVTNBC2QP46qIQg7NVgDYoXYqbuuj35lfSALndtkKJwWnqrH9r6xKHaKqjmpDK3XdmkGvHE1P1Xg=',
}


class PersonFamily(models.Model):
    _name = "person.family"
    _description = "Person Family"
    _order = 'name'

    name = fields.Char(string="Family Name")
    person_id = fields.Many2one('res.partner', string="Parent")
    family_id = fields.Many2one('res.partner', string="Family")
    parent = fields.Boolean(string="Parent")
    student = fields.Boolean(string="Student")

    def name_get(self):
        result = []
        for record in self:
            name = "%s, %s" % (record.family_id.name, record.person_id.name)  # Customize this format as needed
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
    @api.model
    def get_person_family(self):
        country_code = ""
        baseURL = BASE_URL_PERSON_FAMILY
        pageSize = self.make_request(BASE_URL_PERSON_FAMILY)
        get_total_person_family_records = pageSize['rowCount']
        params = urllib.parse.urlencode({
            'PageSize': f'{get_total_person_family_records}',
        })
        base_student_url = f"{baseURL}?{params}"
        data_person_family = self.make_request(base_student_url)
        counter = 0
        all_person_family = []
        try:
            list_of_person_family = data_person_family['results']
            for record in list_of_person_family:
                person_id = record.get('personId')
                family_id = record.get('familyId')
                # # Find the corresponding parent and student records
                person_partner = self.env['res.partner'].search([('facts_id', '=', person_id)])
                family_partner = self.env['res.partner'].search(
                    [('facts_id', '=', family_id), ('company_type', '=', 'company')])
                if person_partner and family_partner:
                    person_family_info = self.env['person.family'].search([
                        ('person_id.facts_id', '=', person_id),
                        ('family_id.facts_id', '=', family_id),
                    ])
                    if not person_family_info:
                        person_family = person_family_info.create({
                            'person_id': person_partner.id,
                            'family_id': family_partner.id,
                            'name': person_partner.first_name + " " + person_partner.last_name,
                            'parent': record.get('parent'),
                            'student': record.get('student')

                        })
                        counter += 1
                        print("Total number of family students created", counter)
                        all_person_family.append(person_family.id)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Success!',
                    'message': f'{len(all_person_family)} Person Family fetched.',
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
