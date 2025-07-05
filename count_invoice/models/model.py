from odoo import api, fields, models
from odoo.exceptions import UserError
# from dateutil.relativedelta import relativedelta



class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    invoice_ref=fields.Many2one('sale.subscription',string="Invoice Ref")
    