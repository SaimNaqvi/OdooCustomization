{
    'name': 'Student Admissions',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Student Registration/Admission Form',
    'description': """Student Registration/Admission on Form with Branch Selection""",
    'depends': ['website', 'base', 'bi_branch_base'],
    'data': [
        'data/mail_template_data.xml',
        'data/email_template_for_challan.xml',
        'views/student_registration_form.xml',
        'views/admission_form.xml',
        'views/inherit_contact_us_template.xml',
        # 'views/custom_login_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'students_admission/static/src/js/registration_form.js',
            'students_admission/static/src/js/admission_form.js',
        ],
    },
    'installable': True,
    'application': True,
}
