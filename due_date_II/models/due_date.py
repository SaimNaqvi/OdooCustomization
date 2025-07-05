from odoo import models, fields, api, exceptions
from datetime import timedelta

class MyModel(models.Model):
    _inherit = "account.move"
    
    # due_date_I = fields.Date(string='Due Date I Custom', required=True, date_format='%d-%m-%Y')
    due_date_II = fields.Date(string='Due Date II', date_format='%d-%m-%Y')

    # ---------- Changes made by Syed Owais Noor ----------

    @api.onchange('invoice_date')
    def update_due_date_II(self):
        for rec in self:
            if rec.invoice_date:
                rec.invoice_date_due = rec.invoice_date + timedelta(days=9)
                rec.due_date_II = rec.invoice_date_due + timedelta(days=7)

    @api.onchange('invoice_date_due')
    def update_invoice_payment_term_id(self):
        for rec in self:
            if rec.invoice_date:
                rec.due_date_II = rec.invoice_date_due + timedelta(days=7)

    # -----------------------------------------------------


    # @api.depends('due_date_I')
    # def _compute_due_date_II(self):
    #     self.due_date_I = self.invoice_date_due
    #     for record in self:
    #         record.due_date_II = record.due_date_I + timedelta(days=10)

    # Commented by Syed Owais Noor
    # @api.depends('due_date_I', 'invoice_date')
    # def _compute_due_date_II(self):
    #     # self.invoice_date_due = self.invoice_date
    #     for record in self:
    #         if record.invoice_date:
    #             record.due_date_II = record.invoice_date + timedelta(days=10)
    #         # elif record.invoice_date_due:
    #         #     record.due_date_I = record.invoice_date
    #         #     record.due_date_II = record.due_date_I + timedelta(days=10)
    #         else:
    #             record.invoice_date = None
    #             record.invoice_date_due = None
    #             record.due_date_II = None
    
    
            
                # record.due_date_II = fields.Date.from_string(record.due_date_I) + timedelta(days=10)
        # for record in self:
        # for record in self:
        #     due_date_I_str = datetime.strptime(record.due_date_I, '%Y-%m-%d').strftime('%d-%m-%Y')
        #     record.due_date_II = datetime.strptime(due_date_I_str, '%d-%m-%Y') + timedelta(days=10)
    
        # due_date_I = fields.Date(string='Due Date I Custom', required=True, date_format='%Y-%m-%d')
        # due_date_II = fields.Date(string='Due Date II', compute='_compute_due_date_II', date_format='%Y-%m-%d')

        # @api.depends('due_date_I')
        # def _compute_due_date_II(self):
        #     for record in self:
        #         due_date_I = record.due_date_I
        #         due_date_I_datetime = datetime.strptime(due_date_I, '%Y-%m-%d')
        #         due_date_II_datetime = due_date_I_datetime + timedelta(days=10)
        #         record.due_date_II = due_date_II_datetime.strftime('%Y-%m-%d')
    
    
    
    
    # _name = 'my.model'
    # _description = 'Description of my model'

    # name = fields.Char(string='Name', required=True)
    # description = fields.Text(string='Description')
    # is_active = fields.Boolean(string='Active', default=True)

    # @api.multi
    # def do_something(self):
    #     # Method implementation goes here
    #     return True