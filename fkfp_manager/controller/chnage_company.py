# controllers/session.py
from odoo.addons.web.controllers.main import Session
from odoo import http
from odoo.http import request


class CustomSession(Session):

    @http.route('/web/session/change_company', type='json', auth="user")
    def change_company(self, company_id, **kwargs):
        # Call the original method to switch session context
        result = super(CustomSession, self).change_company(company_id, **kwargs)

        # Persist the selected company_id to the user record
        user = request.env.user
        user.sudo().write({'company_id': company_id})

        return result
