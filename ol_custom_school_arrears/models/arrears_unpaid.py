from odoo import api, fields, models, _

from odoo.exceptions import UserError
from datetime import date

class unpaid_arrears(models.Model):
    _inherit = "account.move"

    unpaid_std_ids = fields.Many2many(
        comodel_name='account.move',
        compute='_compute_unpaid_invoice_students',
        string='UnPaid Invoice Ids Students',

    )

    is_overdue=fields.Boolean(string="Over Due",default=False,compute='_compute_check_duedate')
    current_date=fields.Date(string="Current Date",default=date.today()) 
    is_overdue2=fields.Boolean(string="Over Due",default=False)


    # @api.model
    # def update_current_date(self):
    #     today = date.today()
    #     records_to_update = self.search([('current_date', '!=', today)])
    #     records_to_update.write({'current_date': today})

    # @api.depends('current_date', 'invoice_date_due')
    def _compute_check_duedate(self):
        for rec in self:
            rec.is_overdue=False
            rec.is_overdue2=False
            todays_date=date.today()
            if rec.invoice_date_due:
                if todays_date > rec.invoice_date_due:
                    rec.is_overdue=True
                    rec.is_overdue2=True
              
                

    def _compute_unpaid_invoice_students(self):
        for std_rec in self:
            std_rec.unpaid_std_ids = self.env['account.move'].search([("move_type", "=", "out_invoice"),
                                                                    ("partner_id", "=", std_rec.partner_id.id), 
                                                                    ("payment_state", "!=", "in_payment"), 
                                                                    ("id", "!=", std_rec.id),
                                                                    ("state","=","posted")])

    def unpaid_amount(self):

        total = 0
        invoice_lines = []
        for record in self:

            #raise UserError(record.partner_id.unpaid_invoices)
            if len(record.partner_id.parent_id.unpaid_invoices) > 1:
                #raise UserError(invoice_lines)

                #raise UserError(invoice_lines)
                total_unpaid = record.partner_id.total_due
                minus_currunt = abs(total_unpaid-record.amount_residual)
                #raise UserError(minus_currunt)
                product = record.env['product.product'].search(
                    [('id', '=', 53)])
                journal_line_obj = record.env['account.move.line']
                invoice_lines = {
                    'product_id': 53,
                    'name': product.name,
                    'quantity': 1,
                    'price_unit': minus_currunt,
                    'account_id': 410,
                    'move_id': record.id,
                    # 'invoice_line_tax_ids': [(6, 0, [tax.id])],
                }

                record.invoice_line_ids = [(0, 0, invoice_lines)]

                invoice_line_id = journal_line_obj.create(invoice_lines)
