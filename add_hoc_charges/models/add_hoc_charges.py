from odoo import api, fields, models
from odoo.exceptions import UserError
import json
import datetime


class add_hoc_charges_wiz(models.TransientModel):
    _name = 'sale.add_hoc_charges_wiz'
    plan_ids = fields.Many2many('sale.subscription', string='sale_subscription')
    product_id = fields.Many2one('product.product', string='Product')
    installment_names = fields.Many2many('installment.name', string="Billing Cycle")

    unit_price = fields.Integer("Unit Price")
    currency_id = fields.Many2one('res.currency', "Currency")
    quantity = fields.Integer("Quantity")

    operation = fields.Selection([('add', 'Add'), ('update', 'Update')], "Operation")

    def apply(self):
        if self.operation == "add":
            val = ""
            lis1t = []
            list2 = []
            for t_plan in self.plan_ids:
                # raise UserError(t_plan)
                for p in t_plan.recurring_invoice_line_ids:
                    if p.product_id == self.product_id:
                        lis1t.append(t_plan)
                        val = "yes"
            if lis1t:
                for li in lis1t:
                    udid = li.partner_id.facts_id
                    name = li.partner_id.name
                    stu = str(udid) + " " + name + " "
                    list2.append(stu)
                raise UserError("Charge is Already Exist in the following students: " + str(list2)[1:-1])
            else:
                self.add()
            # for t_plan in self.plan_ids:
            #     for p_lines in t_plan.line_ids:
            #         val=""
            #         if p_lines.product_id == self.product_id:
            #             #raise UserError("already exist in plan")
            #             val="yes"
            #         else:
            #             val="no"
            # if val=="yes":
            #     raise UserError("Charge is already exist in Tuition Plan!!")
            # else:
            #     self.add()
        else:
            self.update()

    def add(self):
        lst = []
        lst_fc = []
        for plan in self.plan_ids:
            names = [i.name for i in self.installment_names]
            line_months_subscription_line = self.env['x_billing_months'].search([
                ('x_name', 'in', names)])
            # ('sale_subscription_id','=',plan.id)
            linedata = {
                # 'plan_id':plan.id,
                'analytic_account_id': plan.id,
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                # 'account_id':self.product_id.property_account_income_id.id,
                'quantity': self.quantity,
                'line_months_subscription_line': [
                    (6, 0, [i.id for i in line_months_subscription_line if i.x_name in names])],
                'currency_id': self.currency_id.id,
                'price_unit': self.unit_price,
                'uom_id': 1,
            }

            new_plan_line_id = self.env['sale.subscription.line'].create(linedata)
            # line = self.env['sale.subscription.line'].search(
            #     [('analytic_account_id', "=", plan.id), ('product_id', "=", self.product_id.id)])
            # line.write(linedata)
            # raise UserError(str(new_plan_line_id))

    def update(self):
        for plan in self.plan_ids:
            names = [i.name for i in self.installment_names]
            line_months_subscription_line = self.env['x_billing_months'].search([
                ('x_name', 'in', names)])
            # if self.product_id.is_discount_type:
            #     if self.product_id.x_studio_is_fcraw:
            #         sale_subscription=self.env['sale.subscription'].search([('id','=',plan.id)])
            #         if self.unit_price==0:
            #             # sale_subscription["x_studio_fcraw"]=0
            #             sale_subscription["x_studio_fcraw"]=0

            #         if self.unit_price>0:
            #             sale_subscription["x_studio_fcraw"]=1
            #     else:
            #         sale_subscription=self.env['sale.subscription'].search([('id','=',plan.id)])
            #         if self.unit_price==0:
            #             sale_subscription["x_studio_have_discount_1"]=0
            #         if self.unit_price>0:
            #             sale_subscription["x_studio_have_discount_1"]=1

            linedata = {
                'analytic_account_id': plan.id,
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                # 'account_id':self.product_id.property_account_income_id.id,
                'quantity': self.quantity,
                'line_months_subscription_line': [
                    (6, 0, [i.id for i in line_months_subscription_line if i.x_name in names])],
                'uom_id': 1,
                'price_unit': self.unit_price,

            }
            # line=self.env['sale.subscription.line'].search([('plan_id',"=",plan.id),('product_id',"=",self.product_id.id)])
            line = self.env['sale.subscription.line'].search(
                [('analytic_account_id', "=", plan.id), ('product_id', "=", self.product_id.id)])
            line.write(linedata)
            # raise UserError(str(line))

    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)
        ids = self._context.get("active_ids")
        res["plan_ids"] = [(6, 0, ids)]
        return res


class installment_names(models.Model):
    _name = "installment.name"
    name = fields.Char(string='Name')
