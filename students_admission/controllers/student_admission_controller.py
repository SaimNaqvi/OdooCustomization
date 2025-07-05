from odoo import http
from odoo.http import request
import logging
from datetime import datetime, timedelta
import base64

_logger = logging.getLogger(__name__)


class AdmissionController(http.Controller):

    @http.route('/student/admission', type='http', auth="user", website=True)
    def student_admission_form(self, **kwargs):
        user = request.env.user
        branch_name = user.branch_id.name if user.branch_id else ''
        values = {
            'branch_name': branch_name,
        }
        return request.render("students_admission.student_admission_form", values)

    @http.route('/student/admission/search', type='json', auth="user", methods=['POST'])
    def search_student(self, reg_number, branch_id):
        student = request.env['res.partner'].sudo().search([
            ('branch_id.name', '=', branch_id),
            ('reg_number', '=', reg_number),
        ], limit=1)
        # state_id = student.state_id
        state_id = request.env['res.country.state'].sudo().search([('code', '=', 'PK-PB')])
        if student:
            # Filter only the "Father" and "Mother" relationships
            parent_relationships = student.student_relationship_ids.filtered(
                lambda r: r.relationship_type in ['father', 'mother']
            )
            # Separate Father and Mother data
            father = parent_relationships.filtered(lambda r: r.relationship_type == 'father')
            mother = parent_relationships.filtered(lambda r: r.relationship_type == 'mother')
            # Filter emergency contacts based on the is_emergency_contact Boolean
            emergency_contacts = student.student_relationship_ids.filtered(
                lambda r: r.is_emergency_contact
            )
            ec1 = emergency_contacts[0] if len(emergency_contacts) > 0 else None
            ec2 = emergency_contacts[1] if len(emergency_contacts) > 1 else None
            # Fetch sibling data
            siblings = []
            siblings = student.student_relationship_ids.mapped('parent_id.student_ids').mapped('student_id').filtered(
                lambda s: s.reg_number != reg_number  # Exclude the current student
            )
            # Siblings information
            sibling1 = siblings[0] if len(siblings) > 0 else None
            sibling2 = siblings[1] if len(siblings) > 1 else None
            sibling3 = siblings[2] if len(siblings) > 2 else None

            def safe_get(value):
                return value if value else ''

            return {
                'stu_firstname': safe_get(student.first_name),
                'stu_lastname': safe_get(student.last_name),
                'stu_reg_no': safe_get(student.reg_number),
                'stu_class': safe_get(student.current_grade_selection),
                'stu_section': safe_get(student.new_homeroom),
                'stu_status': safe_get(student.current_enroll_status.name),
                'test_date': safe_get(student.test_date),
                'test_status': safe_get(student.test_status),
                'stu_gender': safe_get(student.gender),
                'stu_religion': safe_get(student.religion),
                'stu_dob': safe_get(student.dob),
                'stu_address': safe_get(student.street),
                'stu_city': safe_get(student.city),
                'stu_state': safe_get(student.state_id.name),
                'stu_cnic': safe_get(student.b_form),
                'stu_phone': safe_get(student.phone),
                'stu_email': safe_get(student.email),
                'stu_pre_school_name': safe_get(student.previous_school),
                'admission_date': safe_get(student.admission_date),
                'par1_qtn1': safe_get(student.comment),
                # Parent/Guardian 1
                'par1_relation_type': safe_get(father.relationship_type if father else ''),
                'par1_salutation': safe_get(father.parent_id.parent_salutation if father else ''),
                'par1_firstname': safe_get(father.parent_id.first_name if father else ''),
                'par1_lastname': safe_get(father.parent_id.last_name if father else ''),
                'par1_gender': safe_get(father.parent_id.gender if father else ''),
                'par1_religion': safe_get(father.parent_id.religion if father else ''),
                'par1_dob': safe_get(father.parent_id.dob if father else ''),
                'par1_cnic': safe_get(father.parent_id.cnic if father else ''),
                'par1_phone': safe_get(father.parent_id.phone if father else ''),
                'par1_email': safe_get(father.parent_id.email if father else ''),
                'par1_edu_level': safe_get(father.parent_id.parent_education if father else ''),
                'par1_occupation': safe_get(father.parent_id.parent_occupation if father else ''),
                # Parent/Guardian 2
                'par2_relation_type': safe_get(mother.relationship_type if mother else ''),
                'par2_salutation': safe_get(mother.parent_id.parent_salutation if mother else ''),
                'par2_firstname': safe_get(mother.parent_id.first_name if mother else ''),
                'par2_lastname': safe_get(mother.parent_id.last_name if mother else ''),
                'par2_gender': safe_get(mother.parent_id.gender if mother else ''),
                'par2_religion': safe_get(mother.parent_id.religion if mother else ''),
                'par2_dob': safe_get(mother.parent_id.dob if mother else ''),
                'par2_cnic': safe_get(mother.parent_id.cnic if mother else ''),
                'par2_phone': safe_get(mother.parent_id.phone if mother else ''),
                'par2_email': safe_get(mother.parent_id.email if mother else ''),
                'par2_edu_level': safe_get(mother.parent_id.parent_education if mother else ''),
                'par2_occupation': safe_get(mother.parent_id.parent_occupation if mother else ''),
                # Emergency Contact 1 Information
                'ec1_relation_type': safe_get(ec1.relationship_type if ec1 else ''),
                'ec1_firstname': safe_get(ec1.parent_id.first_name if ec1 else ''),
                'ec1_lastname': safe_get(ec1.parent_id.last_name if ec1 else ''),
                'ec1_phone': safe_get(ec1.parent_id.phone if ec1 else ''),
                # Emergency Contact 2 Information
                'ec2_relation_type': safe_get(ec2.relationship_type if ec2 else ''),
                'ec2_firstname': safe_get(ec2.parent_id.first_name if ec2 else ''),
                'ec2_lastname': safe_get(ec2.parent_id.last_name if ec2 else ''),
                'ec2_phone': safe_get(ec2.parent_id.phone if ec2 else ''),
                # Sibling 1 Information
                'sib1_branch_name': safe_get(sibling1.branch_id.name if sibling1 else ''),
                'sib1_roll_no': safe_get(sibling1.student_code if sibling1 else ''),
                'sib1_class': safe_get(sibling1.current_grade_selection if sibling1 else ''),
                'sib1_firstname': safe_get(sibling1.first_name if sibling1 else ''),
                'sib1_lastname': safe_get(sibling1.last_name if sibling1 else ''),
                # Sibling 2 Information
                'sib2_branch_name': safe_get(sibling2.branch_id.name if sibling2 else ''),
                'sib2_roll_no': safe_get(sibling2.student_code if sibling2 else ''),
                'sib2_class': safe_get(sibling2.current_grade_selection if sibling2 else ''),
                'sib2_firstname': safe_get(sibling2.first_name if sibling2 else ''),
                'sib2_lastname': safe_get(sibling2.last_name if sibling2 else ''),
                # Sibling 3 Information
                'sib3_branch_name': safe_get(sibling3.branch_id.name if sibling3 else ''),
                'sib3_roll_no': safe_get(sibling3.student_code if sibling3 else ''),
                'sib3_class': safe_get(sibling3.current_grade_selection if sibling3 else ''),
                'sib3_firstname': safe_get(sibling3.first_name if sibling3 else ''),
                'sib3_lastname': safe_get(sibling3.last_name if sibling3 else ''),
            }
        else:
            return {}

    @http.route('/student/admission/submit', type='http', auth="user", website=True, csrf=False, methods=['POST'])
    def submit_admission_form(self, **post):
        current_user = request.env.user
        branch = current_user.branch_id
        student = request.env['res.partner'].sudo().search([
            ('reg_number', '=', post.get('stu_reg_no_search')),
            ('branch_id', '=', int(branch.id))
        ], limit=1)
        enrollment_status = request.env['enrollment.status'].sudo().search([('name', '=', 'Admissions')], limit=1)
        country = request.env['res.country'].sudo().search([('name', '=', 'Pakistan')])
        current_grade = student.current_grade_selection
        state = request.env['res.country.state'].sudo().search([('code', '=', 'PK-PB')])
        if student:
            student_name = post.get('stu_firstname') + ' ' + post.get('stu_lastname')
            student.sudo().write({
                'name': student_name,
                'first_name': post.get('stu_firstname'),
                'last_name': post.get('stu_lastname'),
                'email': post.get('stu_email'),
                'phone': post.get('stu_phone'),
                'current_enroll_status': enrollment_status.id,
                'current_grade_selection': post.get('stu_class'),
                'new_homeroom': post.get('stu_section'),
                'religion': post.get('stu_religion'),
                'gender': post.get('stu_gender'),
                'dob': post.get('stu_dob'),
                'b_form': post.get('stu_cnic'),
                'street': post.get('stu_address'),
                'city': post.get('stu_city'),
                'state_id': state.id,
                'country_id': country.id,
                'previous_school': post.get('stu_pre_school_name'),
                'admission_date': post.get('par_ack_date')
                # 'previous_school': post.get('stu_pre_school_class'),

            })
            parent1 = request.env['res.partner'].sudo().search(
                [('cnic', '=', post.get('par1_cnic'))], limit=1)
            if parent1:
                parent_name = post.get('par1_firstname') + ' ' + post.get('par1_lastname')
                # Update Parent 1's record
                parent1.sudo().write({
                    'name': parent_name,
                    'first_name': post.get('par1_firstname'),
                    'last_name': post.get('par1_lastname'),
                    'email': post.get('par1_email'),
                    'phone': post.get('par1_phone'),
                    'parent_occupation': post.get('par1_occupation'),
                    'street': post.get('stu_address'),
                    'gender': post.get('par1_gender'),
                    # 'religion': post.get('par1_religion'),
                    'dob': post.get('par1_dob') if post.get('par1_dob') else False,
                    'cnic': post.get('par1_cnic'),
                    'parent_education': post.get('par1_edu_level'),
                    # 'parent_salutation': post.get('par1_salutation'),
                    # Add other fields as needed
                })
                relationship1 = student.student_relationship_ids.filtered(lambda r: r.parent_id == parent1)
                if relationship1:
                    # Update the existing relationship
                    relationship1.sudo().write({
                        'relationship_type': post.get('par1_relation_type'),  # Update the relationship type
                    })
                else:
                    # Create new relationship with Parent 1
                    student.sudo().write({
                        'student_relationship_ids': [(0, 0, {
                            'parent_id': parent1.id,
                            'relationship_type': post.get('par1_relation_type'),  # Set the relationship type
                        })],
                    })
            else:
                parent_name = post.get('par1_firstname') + ' ' + post.get('par1_lastname')
                # Create a new Parent 1 record and link it to the student
                parent1 = request.env['res.partner'].sudo().create({
                    'name': parent_name,
                    'email': post.get('par1_email'),
                    'phone': post.get('par1_phone'),
                    'parent_occupation': post.get('par1_occupation'),
                    'street': post.get('stu_address'),
                    'gender': post.get('par1_gender'),
                    'religion': post.get('par1_religion'),
                    'dob': post.get('par1_dob') if post.get('par1_dob') else False,
                    'cnic': post.get('par1_cnic'),
                    'parent_education': post.get('par1_edu_level'),
                    'parent_salutation': post.get('par1_salutation'),
                    'is_parent': True,
                })
                # Link Parent 1 to the student
                student.sudo().write({
                    'student_relationship_ids': [(0, 0, {
                        'parent_id': parent1.id,
                        'relationship_type': post.get('par1_relation_type'),
                    })],
                })
            parent2 = request.env['res.partner'].sudo().search(
                [('cnic', '=', post.get('par2_cnic'))], limit=1)
            if parent2:
                parent_name = post.get('par2_firstname') + ' ' + post.get('par2_lastname')
                # Update Parent 2's record
                parent2.sudo().write({
                    'name': parent_name,
                    'first_name': post.get('par2_firstname'),
                    'last_name': post.get('par2_lastname'),
                    'email': post.get('par2_email'),
                    'phone': post.get('par2_phone'),
                    'parent_occupation': post.get('par2_occupation'),
                    'street': post.get('stu_address'),
                    'gender': post.get('par2_gender'),
                    'religion': post.get('par2_religion'),
                    'dob': post.get('par2_dob') if post.get('par2_dob') else False,
                    'cnic': post.get('par2_cnic'),
                    'parent_education': post.get('par2_edu_level'),
                    'parent_salutation': post.get('par2_salutation'),
                    # Add other fields as needed
                })
                # Check if the relationship with Parent 2 exists for the student
                relationship2 = student.student_relationship_ids.filtered(lambda r: r.parent_id == parent2)

                if relationship2:
                    # Update the existing relationship
                    relationship2.sudo().write({
                        'relationship_type': post.get('par2_relation_type'),  # Update the relationship type
                    })
                else:
                    # Create new relationship with Parent 2
                    student.sudo().write({
                        'student_relationship_ids': [(0, 0, {
                            'parent_id': parent2.id,
                            'relationship_type': post.get('par2_relation_type'),  # Set the relationship type
                        })],
                    })
            else:
                parent_name = post.get('par2_firstname') + ' ' + post.get('par2_lastname')
                # Create a new Parent record and link it to the student
                parent2 = request.env['res.partner'].sudo().create({
                    'name': parent_name,
                    'first_name': post.get('par2_firstname'),
                    'last_name': post.get('par2_lastname'),
                    'email': post.get('par2_email'),
                    'phone': post.get('par2_phone'),
                    'parent_occupation': post.get('par2_occupation'),
                    'street': post.get('stu_address'),
                    'gender': post.get('par2_gender'),
                    'religion': post.get('par2_religion'),
                    'dob': post.get('par2_dob') if post.get('par2_dob') else False,
                    'cnic': post.get('par2_cnic'),
                    'parent_education': post.get('par2_edu_level'),
                    'parent_salutation': post.get('par2_salutation'),
                    'is_parent': True,
                })
                # Link Parent 2 to the student
                student.sudo().write({
                    'student_relationship_ids': [(0, 0, {
                        'parent_id': parent2.id,
                        'relationship_type': post.get('par2_relation_type'),
                    })],
                })

            # Create emergency relationship for student and link to that student
            ec1 = request.env['res.partner'].sudo().search(
                ['|', ('phone', '=', post.get('ec1_phone')), ('mobile', '=', post.get('ec1_phone'))], limit=1)
            ec1_name = post.get('ec1_firstname') + ' ' + post.get('ec1_lastname')
            if ec1:
                # Update Emergency Contact 1's record
                ec1.sudo().write({
                    'name': ec1_name,
                    'first_name': post.get('ec1_firstname'),
                    'last_name': post.get('ec1_lastname'),
                    'phone': post.get('ec1_phone'),
                    # Add other fields as needed
                })
                # Check if the relationship with EC 1 exists for the student
                ec_relation1 = student.student_relationship_ids.filtered(lambda r: r.parent_id == ec1)

                if ec_relation1:
                    # Update the existing relationship
                    ec_relation1.sudo().write({
                        'relationship_type': post.get('ec1_relation_type'),  # Update the relationship type
                        'is_emergency_contact': True
                    })
                else:
                    # Create new relationship with EC 1
                    student.sudo().write({
                        'student_relationship_ids': [(0, 0, {
                            'parent_id': ec1.id,
                            'relationship_type': post.get('ec1_relation_type'),
                            'is_emergency_contact': True,
                        })],
                    })
            else:
                title = request.env['res.partner.title'].sudo().search([('name', '=', 'Emergency Contact')])
                # Create a new EC 1 record and link it to the student
                ec1 = request.env['res.partner'].sudo().create({
                    'name': ec1_name,
                    'first_name': post.get('ec1_firstname'),
                    'last_name': post.get('ec1_lastname'),
                    'phone': post.get('ec1_phone'),
                    'title': title.id,
                })
                # Link EC 1 to the student
                student.sudo().write({
                    'student_relationship_ids': [(0, 0, {
                        'parent_id': ec1.id,
                        'relationship_type': post.get('ec1_relation_type'),
                        'is_emergency_contact': True,
                    })],
                })
            ec2 = request.env['res.partner'].sudo().search(
                ['|', ('phone', '=', post.get('ec2_phone')), ('mobile', '=', post.get('ec2_phone'))], limit=1)
            ec2_name = post.get('ec2_firstname') + ' ' + post.get('ec2_lastname')
            if post.get('ec2_phone'):
                if ec2:
                    # Update Emergency Contact 2's record
                    ec2.sudo().write({
                        'name': ec2_name,
                        'first_name': post.get('ec2_firstname'),
                        'last_name': post.get('ec2_lastname'),
                        'phone': post.get('ec2_phone'),
                        # Add other fields as needed
                    })
                    # Check if the relationship with EC 2 exists for the student
                    ec_relation2 = student.student_relationship_ids.filtered(lambda r: r.parent_id == ec2)

                    if ec_relation2:
                        # Update the existing relationship
                        ec_relation2.sudo().write({
                            'relationship_type': post.get('ec2_relation_type'),
                            'is_emergency_contact': True,
                        })
                    else:
                        # Create new relationship with EC 2
                        student.sudo().write({
                            'student_relationship_ids': [(0, 0, {
                                'parent_id': ec2.id,
                                'relationship_type': post.get('ec2_relation_type'),
                                'is_emergency_contact': True,
                            })],
                        })
                else:
                    # Create a new Emergency Contact record and link it to the student
                    title = request.env['res.partner.title'].sudo().search([('name', '=', 'Emergency Contact')])
                    ec2 = request.env['res.partner'].sudo().create({
                        'name': ec2_name,
                        'first_name': post.get('ec2_firstname'),
                        'last_name': post.get('ec2_lastname'),
                        'phone': post.get('ec2_phone'),
                        'title': title.id,

                    })
                    # Link EC 2 to the student
                    student.sudo().write({
                        'student_relationship_ids': [(0, 0, {
                            'parent_id': ec2.id,
                            'relationship_type': post.get('ec2_relation_type'),
                            'is_emergency_contact': True,
                        })],
                    })
            if post.get('par1_qtn1'):
                student.sudo().write({
                    'comment': post.get('par1_qtn1')
                })
            if post.get('stu_con'):
                student.sudo().write({
                    'concession_comment': post.get('stu_con'),

                })

            if post.get('admission_date') and post.get('parent_relation_type'):
                student.sudo().write({
                    'admission_date': post.get('admission_date'),
                    # 'parent_relation_type': post.get('parent_relation_type'),
                })
            # Handle file attachment
            # Handle file uploads
            files = [
                ('stu_admission_form', 'Admission Form'),
                ('stu_birth_cert_doc', 'Birth Certificate'),
                ('stu_b_form_doc', 'Bay Form'),
                ('par1_cnic_doc', 'Father/Guardian CNIC/NICOP/PASSPORT'),
                ('par2_cnic_doc', 'Mother/Guardian CNIC/NICOP/PASSPORT'),
            ]
            for file_field, description in files:
                if file_field in request.httprequest.files:
                    file = request.httprequest.files[file_field]

                    # Check if the file has a valid filename to ensure it's not an empty upload
                    if file.filename:
                        attachment_data = file.read()
                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': file.filename,
                            'type': 'binary',
                            'datas': base64.b64encode(attachment_data),
                            'res_model': 'res.partner',
                            'res_id': student.id,
                            'mimetype': file.content_type,
                            'description': description,
                        })
        products = request.env['product.product'].sudo().search(
            [('name', 'in', ['Admission Fee', 'Annual Fund', 'Security Refundable', 'Tuition Fee']),
             ('branch_id', '=', int(branch.id))])

        # Calculate dates
        invoice_date = datetime.now()
        invoice_date_due = invoice_date + timedelta(days=9)
        billing_month = invoice_date.strftime('%b-%y')

        # Prepare invoice line items
        invoice_lines = []
        for product in products:
            # Ensure the product has an income account
            account_id = product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id
            if not account_id:
                raise ValueError('The product or its category must have an income account defined.')

            # Append product as an invoice line
            invoice_lines.append((0, 0, {
                'product_id': product.id,
                'account_id': account_id,
                'price_unit': product.list_price,
                'name': product.name,
                'quantity': 1,
            }))
        # Get the account journal according to branch name and type sales
        journal = request.env['account.journal'].sudo().search(
            [('branch_id', '=', student.branch_id.id), ('type', '=', 'sale'),
             ('allow_portal_registration', '=', True)], limit=1
        )
        if not journal:
            journal = request.env['account.journal'].sudo().search(
                [('branch_id', '=', student.branch_id.id)], limit=1
            )

        # Create the invoice for the student
        try:
            invoice = request.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'partner_id': student.id,
                'invoice_date': invoice_date,
                'invoice_date_due': invoice_date_due,
                'billingMonth': billing_month,
                'branch_id': student.branch_id.id,
                'journal_id': journal.id,
                'invoice_line_ids': invoice_lines,  # Add all products as line items
            })

            # Update the branch in the journal items
            for line in invoice.line_ids:
                line.branch_id = student.branch_id.id

            # Confirm the invoice
            invoice.sudo().action_post()

            current_user = request.env.user
            if current_user:
                # Generate the fee challan report (PDF)
                report = request.env.ref('ol_custom_challans.report_fee_challan_copy_declare')
                pdf_content, _ = report.sudo()._render_qweb_pdf([invoice.id])
                # Encode the PDF data
                pdf_data = base64.b64encode(pdf_content)
                # Create an attachment for the PDF
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': 'Fee Challan - %s.pdf' % student.name,
                    'type': 'binary',
                    'datas': pdf_data,
                    'store_fname': 'Fee Challan - %s.pdf' % student.name,
                    'mimetype': 'application/pdf',
                    'res_model': 'account.move',
                    'res_id': invoice.id,
                })
                # Fetch the email template and attach the PDF
                # Fetch the email template and attach the PDF
                template = request.env.ref('students_admission.email_template_fee_challan')
                if template:
                    # Prepare email values and add attachment
                    email_values = {
                        'email_to': current_user.partner_id.email,  # Send to the logged-in branch user
                        'attachment_ids': [(4, attachment.id)],  # Attach the fee challan PDF
                    }

                    # Send the email without the default report by not triggering default invoice attachments
                    mail_id = template.sudo().send_mail(invoice.id, email_values=email_values, force_send=False)

                    # Get the mail record and remove any auto-generated invoice attachment
                    mail = request.env['mail.mail'].sudo().browse(mail_id)
                    invoice_attachment = mail.attachment_ids.filtered(lambda att: 'INV' in att.name)

                    if invoice_attachment:
                        mail.attachment_ids = [(3, invoice_attachment.id)]  # Remove the invoice attachment

                    # Force send the mail
                    mail.sudo().send()
            else:
                None
        except Exception as e:
            print("None")

        return request.redirect('/contactus-thank-you')
