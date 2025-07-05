
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError




class AccountPayReg(models.TransientModel):
    _inherit = "account.payment.register"

    late_fee_amt=fields.Float(string='Late Fee',compute='calc_late_fee',store=True)
    without_late_fee_amt=fields.Float(string='Without Late Fee ',compute='calc_late_fee',store=True)
    set_charge=fields.Boolean(string='Change Charge',default=False)
    set_percentage=fields.Boolean(string='Change Percentage',default=False)
    fee_charge=fields.Integer(string='Charge',default=300)
    fee_percent=fields.Integer(string='Percentage', digits='Percentage', widget='percentage',default=10)
    with_late_fee_payment = fields.Float(string='With Late Fee',compute='calc_late_fee',store=True)


    @api.depends('payment_date','fee_charge','fee_percent')
    def calc_late_fee(self):
        for wizard in self: 
            wizard.late_fee_amt=wizard.fee_charge
            wizard.without_late_fee_amt=0
            invoice=""
            late_fee_product = self.env['product.product'].search([('name', '=', 'Late Fee')])
            for line in wizard.line_ids:
                invoice=line.move_id
                break
            if invoice!="":
                foundline=None
                for line in invoice.invoice_line_ids:
                    if line.product_id.name=="Late Fee":
                        foundline=line
                        break
                ##if line is found. removing that latefee from totalfirst .
                if foundline is not None:
                    wizard.without_late_fee_amt=wizard.amount-foundline.price_unit
                else:
                    wizard.without_late_fee_amt=wizard.amount

            if wizard.payment_date:
                pay_date=wizard.payment_date
                now_date=fields.Datetime.now()
                current_date=now_date.date()
                diff=pay_date-current_date

                if pay_date >= invoice.invoice_date_due:
                    if invoice.invoice_date_due <= pay_date:
                        wizard.late_fee_amt=late_fee_product.list_price
                        wizard.with_late_fee_payment = wizard.late_fee_amt + wizard.amount
                        wizard.amount = wizard.amount + wizard.late_fee_amt
                        print(wizard.amount)
                    elif pay_date >= invoice.due_date_II: 
                        bill= self.env['account.move'].search([('name', '=', wizard.communication)], limit=1)                                               
                        wizard.late_fee_amt= ((late_fee_product.list_price + bill.amount_total) * 0.1)+late_fee_product.list_price
                        wizard.with_late_fee_payment = wizard.late_fee_amt + wizard.amount
                else:
                    wizard.late_fee_amt = 0.00

                # if days==0 or days<=7:
                #     wizard.late_fee_amt=0

                # else:
                #     if days>7 and days<21:
                #         wizard.late_fee_amt=wizard.fee_charge
                #         wizard.amount=wizard.amount+wizard.late_fee_amt
                #     else:
                    
                #         wizard.late_fee_amt=wizard.amount*(wizard.fee_percent/100)
                #         wizard.amount=wizard.amount+wizard.late_fee_amt

    def action_create_payments(self):
        # Retrieve the late fee amount from the wizard field
        
        
        # Check if the late fee amount is greater than zero
        if self.late_fee_amt > 0:
           
            # Retrieve the invoice from the context
            active_id = self._context.get('active_id')
            invoice = self.env['account.move'].browse(active_id)
            
            # Create a new invoice line for the late fee product
            late_fee_product = self.env['product.product'].search([('name', '=', 'Late Fee')])
            late_fee_line = {
                'product_id': late_fee_product.id,
                'name': late_fee_product.name,
                'price_unit': self.late_fee_amt,
                'quantity': 1,
                # 'account_id': invoice.invoice_line_ids[0].account_id.id,
            }
            
            # Add the late fee line to the invoice
            invoice.write({'invoice_line_ids': [(0, 0, late_fee_line)]})
            
        # Call the original method to register the payment
        return super(AccountPayReg, self).action_create_payments()

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_id = fields.Char(
        string='Invoice',
        related='move_id.display_name',
        readonly=True,
    )
    late_fee_amt=fields.Float(string='Late Fee',compute='add_late_fee')
    without_late_fee_amt=fields.Float(string='Without Late Fee ',compute='add_late_fee')

    def add_late_fee(self):
        self.late_fee_amt=0
        self.without_late_fee_amt=0
        string=self.invoice_id
        invoice_ref = string.split("(")[1].split(")")[0]
        invoice = self.env['account.move'].search([('name', '=', invoice_ref)])
        for line in invoice.invoice_line_ids:
            if line.product_id.name=='Late Fee':
                self.late_fee_amt=line.price_unit
                self.without_late_fee_amt=self.amount-self.late_fee_amt



  
        




#