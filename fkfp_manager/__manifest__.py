{
    'name': 'FKFP Manager',
    'category': 'Sales/CRM',
    'sequence': -100,
    'summary': 'Centralize your address book',
    'description': """
        This module gives you a quick view of your Fkfp manager directory, accessible from your home page.
        You can track your vendors, customers and other contacts.
    """,
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/staff_sequence.xml',
        # 'data/res_partner_record_rule.xml',
        'views/fkfp_views.xml',
        'views/fields.xml',
        'views/inherit_res_company_views.xml',
        'views/fkfp_donor.xml',
        'views/fkfp_staff.xml',
        'views/vam.xml',
        'views/smile.xml',
        'views/micro_finance.xml',
        'views/photo_upload_wizard_view.xml',
        'views/document_upload_wizard_view.xml',
        'wizard/send_whatsapp_wizard_views.xml',
        'reports/report_action.xml',
        'reports/report_fkfp_manager_cv.xml',
        # 'views/new_form.xml',
        # 'views/auto.xml',
        # 'views/cost_form.xml',

    ],
    'qweb': [
        # 'static/src/css/style.css',
    ],
    'application': True,
    'license': 'LGPL-3',

    'assets': {
        'web.assets_backend': [
            'web/static/lib/jquery/jquery.js',
            'fkfp_manager/static/lib/inputmask/jquery.inputmask.min.js',
            'fkfp_manager/static/src/js/photo_gallery_buttons.js',
            'fkfp_manager/static/src/xml/photo_gallery_buttons.xml',
            'fkfp_manager/static/src/js/document_buttons.js',
            'fkfp_manager/static/src/xml/document_buttons.xml',

        ],
    }

}
