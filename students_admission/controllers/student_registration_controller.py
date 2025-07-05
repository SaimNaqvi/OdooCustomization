from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import logging
import base64


_logger = logging.getLogger(__name__)


class StudentRegistrationController(http.Controller):
    def auto_reg_number(self, branch):
        branch = request.env['res.branch'].browse(branch)
        if branch:
            set_student_code = branch.set_student_code if branch.set_student_code else 0

            # Direct SQL query to get the maximum reg_number for the branch
            query = """
                        SELECT MAX(CAST(reg_number AS INTEGER))
                        FROM res_partner
                        WHERE branch_id = %s AND is_student = TRUE AND reg_number IS NOT NULL
                    """
            request.env.cr.execute(query, (branch.id,))
            result = request.env.cr.fetchone()

            # Extracting the maximum registration number from the result
            last_student_code = result[0] if result and result[0] is not None else set_student_code

            new_student_reg_number = last_student_code + 1
            return new_student_reg_number

    @http.route('/student/registration', type='http', auth="user", website=True)
    def student_registration_form(self, **kwargs):
        user = request.env.user
        branch_name = user.branch_id.name if user.branch_id else ''
        values = {
            'branch_name': branch_name,
        }
        return request.render("students_admission.student_registration_form", values)

    @http.route('/student/student/parent', type='json', auth="user", methods=['POST'])
    def search_register_student_parent(self, parent_cnic_no):
        parent = request.env['res.partner'].sudo().search([('cnic', '=', parent_cnic_no)], limit=1)

        if parent:
            relationship_type = (
                parent.student_ids.mapped('relationship_type')[0]
                if parent.student_ids and parent.student_ids.mapped('relationship_type')
                else False
            )

            return {
                'par_firstname': parent.first_name,
                'par_lastname': parent.last_name,
                'par_gender': parent.gender,
                'par_religion': parent.religion,
                'par_cnic': parent.cnic,
                'par_phone': parent.phone,
                'par_email': parent.email,
                'par_relation_type': relationship_type,
            }
        else:
            return {'error': 'Parent not found'}

    @http.route('/student/registration/submit', type='http', auth="user", website=True, methods=['POST'])
    def student_registration_submit(self, **kwargs):
        branch = request.env['res.branch'].sudo().search([('name', '=', kwargs.get('branch_name'))], limit=1)
        branch_id = int(branch.id)
        student_first_name = kwargs.get('stu_firstname')
        student_last_name = kwargs.get('stu_lastname')
        student_class = kwargs.get('stu_class')
        student_gender = kwargs.get('stu_gender')
        student_religion = kwargs.get('stu_religion')
        student_dob = kwargs.get('stu_dob')
        parent_first_name = kwargs.get('par_firstname')
        parent_last_name = kwargs.get('par_lastname')
        par_salutation = kwargs.get('par_salutation')
        par_gender = kwargs.get('par_gender')
        par_religion = kwargs.get('par_religion')
        par_relation_type = kwargs.get('par_relation_type')
        parent_email = kwargs.get('par_email')
        parent_cnic = kwargs.get('par_cnic')
        parent_phone = kwargs.get('par_phone')
        next_grade_selection = ''
        if student_class == 'nur' or student_class == 'Nur':
            next_grade_number = 'prep'
            next_grade_selection = next_grade_number
        elif student_class == 'prep' or student_class == 'Prep':
            next_grade_number = '1'
            next_grade_selection = next_grade_number

        # Create parent record
        parent_name = parent_first_name + ' ' + parent_last_name
        # Search exsisting Parent
        parent = request.env['res.partner'].sudo().search([('cnic', '=', parent_cnic)], limit=1)
        if parent:
            parent.sudo().write({
                'name': parent_name,
                'first_name': parent_first_name,
                'last_name': parent_last_name,
                'email': parent_email,
                'phone': parent_phone,
                'gender': par_gender,
                'religion': par_religion,
            })
        else:
            # Create parent record
            parent = request.env['res.partner'].sudo().create({
                'name': parent_name,
                'first_name': parent_first_name,
                'last_name': parent_last_name,
                'email': parent_email,
                'phone': parent_phone,
                'cnic': parent_cnic,
                'parent_salutation': par_salutation,
                'gender': par_gender,
                'religion': par_religion,
                'is_parent': True,
                'branch_id': branch_id,

                'title': request.env['res.partner.title'].search([('name', '=', 'Parent')]).id,
            })
        student_reg_number = self.auto_reg_number(branch_id)
        # Convert the date to the desired format and store it as a string
        student_dob_formatted = False
        try:
            if student_dob:
                # Parse the date string according to its input format '%d/%m/%Y'
                parsed_date = datetime.strptime(student_dob, '%d/%m/%Y')  # '02/11/2009' -> datetime object
                # Convert it to the desired format '%Y-%m-%d' for storage
                student_dob_formatted = parsed_date.strftime('%Y-%m-%d')  # datetime object -> '2009-11-02'
        except ValueError as e:
            # Log the error for debugging
            _logger.error(f"Date conversion error: {str(e)}")
            # Handle incorrect date format with a redirect or an error page
            return

        # Get default receivable and payable accounts
        # receivable_account = request.env['account.account'].sudo().search([('code', '=', '1210001')])
        # payable_account = request.env['account.account'].sudo().search([('code', '=', '21100000')])

        # Create student record linked to the parent
        student_name = student_first_name + ' ' + student_last_name

        student = request.env['res.partner'].sudo().create({
            'name': student_name,
            'first_name': student_first_name,
            'last_name': student_last_name,
            'current_grade_selection': student_class,
            'gender': student_gender,
            'religion': student_religion,
            'dob': student_dob_formatted if student_dob_formatted else False,
            'next_grade_selection': next_grade_selection if next_grade_selection is not '' else student_class,
            'branch_id': branch_id,
            'is_student': True,
            'reg_number': student_reg_number,
            'title': request.env['res.partner.title'].search([('name', '=', 'Student')]).id,
            'current_enroll_status': request.env['enrollment.status'].sudo().search([('name', '=', 'Registration')], limit=1).id,
            'next_enroll_status': request.env['enrollment.status'].sudo().search([('name', '=', 'Admissions')], limit=1).id,
            'student_relationship_ids': [(0, 0, {
                'parent_id': parent.id,
                'relationship_type': par_relation_type,
            })],
        })
        # Fetch the selected fee charges
        product = request.env['product.product'].sudo().search(
            [('name', '=', 'Registration Fee'), ('branch_id', '=', branch_id)], limit=1)

        # Calculate dates
        invoice_date = datetime.now()
        invoice_date_due = invoice_date + timedelta(days=9)
        billing_month = invoice_date.strftime('%b-%y')

        # Ensure the product has an income account
        account_id = product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id

        if not account_id:
            raise ValueError('The product or its category must have an income account defined.')

        # get the account journal according to branch name and type sales
        journal = request.env['account.journal'].sudo().search(
            [('branch_id', '=', student.branch_id.id), ('type', '=', 'sale'), ('allow_portal_registration', '=', True)])
        if not journal:
            journal = request.env['account.journal'].sudo().search(
                [('branch_id', '=', student.branch_id.id)])
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
                'invoice_line_ids': [(0, 0, {
                    'product_id': product.id,
                    'account_id': account_id,
                    'price_unit': product.list_price,
                    'name': product.name,
                    'quantity': 1,
                })]
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
            # Send email to principal
            template = request.env.ref('students_admission.email_template_new_student_registration')
            if template:
                template.sudo().with_context(
                    email_to='syedsaim.1658@gmail.com'
                ).send_mail(student.id, force_send=True)

        except Exception as e:
            _logger.error('Failed to create invoice: %s', e)
            raise

        return request.redirect('/contactus-thank-you')

    @http.route('/student/registration/search', type='json', auth="user", methods=['POST'])
    def search_registration_student(self, reg_number, branch_id):
        student = request.env['res.partner'].sudo().search([
            ('branch_id.name', '=', branch_id),
            ('reg_number', '=', reg_number),
        ], limit=1)
        if student:
            return {
                'student_name': student.name,
                'stu_reg_num': student.reg_number,
                'stu_firstname': student.first_name,
                'stu_lastname': student.last_name,
                'reg_stu_class': student.current_grade_selection,
                'stu_test_date': student.test_date,
                'stu_test_status': student.test_status,

            }
        else:
            return

    @http.route('/student/registration/update', type='http', auth="user", website=True, csrf=True, methods=['POST'])
    def submit_registration_update(self, **post):
        current_user = request.env.user
        branch = current_user.branch_id
        student = request.env['res.partner'].sudo().search([
            ('reg_number', '=', post.get('stu_reg_no_search')),
            ('branch_id', '=', int(branch.id))
        ], limit=1)
        student.sudo().write({
            'first_name': post.get('reg_stu_firstname'),
            'last_name': post.get('reg_stu_lastname'),
            'test_status': post.get('stu_test_status'),
            'test_date': post.get('stu_test_date'),
            'current_grade_selection': post.get('reg_stu_class'),
        })
        return request.redirect('/contactus-thank-you')
