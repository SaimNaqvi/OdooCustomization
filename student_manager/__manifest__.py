# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Student Manager',
    'category': 'Sales/CRM',
    'sequence': 150,
    'summary': 'Centralize your address book',
    'description': """
This module gives you a quick view of your student manager directory, accessible from your home page.
You can track your vendors, customers and other contacts.
""",
    'depends': ['base', 'mail', 'contacts', 'bi_branch_base', 'purchase','account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_cron_job.xml',
        'views/res_partner_form_view.xml',
        # 'views/staff_view.xml',
        'views/student_relation_views.xml',
        'views/person_family_view.xml',
        'views/res_partner_tree_view.xml',
        'views/pivot_view.xml',
        'views/inherit_contact_view.xml',
        'views/inherit_contact_view.xml',
        # 'views/page_reload.xml',
    ],
    'qweb': [
        'static/src/css/style.css',
    ],
    'application': True,
    'license': 'LGPL-3',

}
