
from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime

class custom_discount_model(models.Model):
    _name = "product.cdiscount"
    product_id = fields.Many2one('product.product', string='Charge on')
    discount_type = fields.Selection([
        ('percentage', 'percentage'),
        ('fixed', 'fixed'),
    ], string='type')
    discount_value = fields.Float('Value')
    parent_product_id=fields.Many2one(comodel_name='product.product', string='parent product')
    parent_template_id=fields.Many2one(comodel_name='product.template', string='parent template')
    @api.onchange('discount_value',"discount_type")
    def _onchange_value(self):
        if self.discount_type=="percentage" and self.discount_value>100:
            raise UserError("percentage cannot be larger then 100")
        

class product_ext(models.Model):
    _inherit = "product.product"
    is_discount_type = fields.Boolean('is_discount_type')
    discount_ids = fields.One2many('product.cdiscount',"parent_product_id", string='Discount')

class template_ext(models.Model):
    _inherit = "product.template"
    is_discount_type = fields.Boolean('is_discount_type')
    discount_ids = fields.One2many('product.cdiscount', "parent_template_id",string='Discount')

class invoice_ext(models.Model):
    _inherit = "account.move"

    def applyDiscount(self):
        
        for rec in self:
            invoice_total_discount=0
            lineDiscounts={}
            for line in rec.invoice_line_ids:
                if line.product_id.is_discount_type:
                    # calculate total discount for this custom discount item
                    line_total_amount_discount=0
                    for discount in line.product_id.discount_ids:
                        discount_amount=0
                        for line1 in rec.invoice_line_ids:
                            if discount.product_id.id==line1.product_id.id:
                                
                                if discount.discount_type=="percentage":
                                    discount_amount+=(discount.discount_value/100)*line1.quantity*line1.price_unit
                                else:
                                    discount_amount+=discount.discount_value*line1.quantity
                            discount_amount=int(discount_amount)
                        #raise UserError(discount_amount)
                        line_total_amount_discount+=discount_amount
                    ##add discount to invoice lines
                    if line_total_amount_discount>0:
                        ##changing invoice line ids 
                        data={
                            "quantity":1,
                            "price_unit":(-1)*line_total_amount_discount
                        }
                        
                        line.with_context(check_move_validity=False).write(data)
                        invoice_total_discount+=line_total_amount_discount
                    lineDiscounts[line.name]=line_total_amount_discount
                    #lineDiscounts[line.price_unit]=(-1)*line_total_amount_discount
                    #raise UserError(line_total_amount_discount)

            ## add the discount to journal lines
            if invoice_total_discount>0:
                ## changing the journal lines
                discount_line=False
                recievable_line=False
                total_credit=0
                for jl in rec.line_ids:
                    total_credit+=jl.credit
                    if jl.account_id.name=="Receivable from Customers":
                        recievable_line=jl
                    if jl.product_id.is_discount_type:
                        amount=lineDiscounts.get(jl.name,None)
                        if amount is None:
                            raise UserError("invalid discount name in journal lines : \""+jl.name+"\". Discount invoice line and discount journal line should have save name."+str(lineDiscounts))
                        # raise UserError("test : "+str(lineDiscounts)+" "+str(invoice_total_discount))
                        jl.with_context(check_move_validity=False).write({"debit":amount,"credit":0})

                customer_recievable_amount = total_credit-invoice_total_discount
                # raise UserError(customer_recievable_amount)

                recievable_line.with_context(check_move_validity=False).write({"debit":customer_recievable_amount,"credit":0})


