import logging
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from datetime import timedelta, datetime


class Subscription_lines(models.Model):
    _name = 'subs.template.lines'
    _order = 'sequence, id'

    sequence = fields.Integer(string="Sequence", default=10)
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description', related="product_id.name")
    line_months = fields.Many2many(
        'x_billing_months', string='Months', related='product_id.x_studio_many2many_field_E1EQQ')
    price_unit = fields.Float(string='Price')
    product_uom_qty = fields.Float(string='Quantity')
    order_id = fields.Many2one('sale.subscription.template',
                               string='subscription template id', index=True, required=True, ondelete='cascade')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for record in self:
            record.price_unit = record.product_id.lst_price
            record.product_uom_qty = 1.0
            record.line_months = record.product_id.x_studio_many2many_field_E1EQQ.ids


class SubscriptionTemplate(models.Model):
    _inherit = 'sale.subscription.template'

    subs_lines = fields.One2many(
        'subs.template.lines', 'order_id', string='Order Lines')

    # Button to trigger fee plan updates
    def update_fee_plans(self):
        # Fetch all subscriptions linked to this template
        fee_plans = self.env['sale.subscription'].search([('template_id', '=', self.id)])

        for plan in fee_plans:
            # Prepare new lines
            new_lines = []
            tuition_fee_lines = []
            other_fee_lines = []

            # Iterate through the template lines
            for line in self.subs_lines:
                subscription_line = {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.product_uom_qty,
                    'uom_id': 1,
                    'price_unit': line.price_unit,
                    'line_months_subscription_line': [(6, 0, line.line_months.ids)],
                }

                # Check if the product is a tuition fee
                if line.product_id.name.lower() == 'tuition fee':
                    tuition_fee_lines.append((0, 0, subscription_line))
                else:
                    other_fee_lines.append((0, 0, subscription_line))

            # Clear old lines in the plan
            plan.recurring_invoice_line_ids = False

            # Add the tuition fee first, followed by other lines
            plan.recurring_invoice_line_ids = tuition_fee_lines + other_fee_lines


class SaleSubscriptionInherit(models.Model):
    _inherit = 'sale.subscription'

    # Changes made in on_change_template_id function ~ Shamoil
    def apply_concession(self):
        current_month = datetime.now().month
        end_month = 12  # December

        # Find billing month records from current month to December
        billing_months = self.env['x_billing_months'].search(
            [('id', '>=', current_month), ('id', '<=', end_month)])

        for rec in self:
            # Filter tuition fee products from subscription
            total_recurring_fee = self.recurring_invoice_line_ids.filtered(
                lambda l: l.product_id.product_tmpl_id.is_discount_type)
            tuition_fee = total_recurring_fee.price_unit
            # Update existing fee plan for new concessions
            for concession in rec.partner_id.student_concessions:
                discount_percentage = concession.discount_value or 0.0
                discount_value = tuition_fee * (discount_percentage / 100)

                existing_lines = rec.recurring_invoice_line_ids.filtered(
                    lambda l: l.product_id == concession.product_id)
                if existing_lines:
                    for line in existing_lines:
                        # line.line_months_subscription_line = [(6, 0, billing_months.ids)]
                        line.price_unit = line.price_unit - discount_value
                else:
                    subscription_line = self.env['sale.subscription.line'].create({
                        'product_id': concession.product_id.id,
                        'name': concession.product_id.name,
                        'quantity': 1,
                        'uom_id': concession.product_id.uom_id.id,
                        'price_unit': discount_value,  # Actual discount will be calculated during invoice creation
                        'line_months_subscription_line': [(6, 0, billing_months.ids)],
                    })
                    self.recurring_invoice_line_ids |= subscription_line

    def update_fee_plans(self):
        # Fetch all subscriptions linked to this template
        fee_template = self.env['sale.subscription.template'].search([('id', '=', self.template_id.id)])

        for plan in self:
            # Prepare new lines
            new_lines = []
            tuition_fee_lines = []
            other_fee_lines = []

            # Iterate through the template lines
            for line in fee_template.subs_lines:
                subscription_line = {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.product_uom_qty,
                    'uom_id': 1,
                    'price_unit': line.price_unit,
                    'line_months_subscription_line': [(6, 0, line.line_months.ids)],
                }

                # Check if the product is a tuition fee
                if line.product_id.name.lower() == 'tuition fee':
                    tuition_fee_lines.append((0, 0, subscription_line))
                else:
                    other_fee_lines.append((0, 0, subscription_line))

            # Clear old lines in the plan
            plan.recurring_invoice_line_ids = False

            # Add the tuition fee first, followed by other lines
            plan.recurring_invoice_line_ids = tuition_fee_lines + other_fee_lines
    def assign_months_to_all_fee_plans(self):
        return self.env['sale.subscription.line'].assign_months_to_all_fee_plans()

    def start_subscription(self):
        for rec in self:
            # Debugging: Ensure we have a valid record
            if not rec:
                continue

            # Debugging: Check the record stage_id before proceeding
            if not rec.stage_id:
                raise ValueError(f"Record {rec.id} has no stage_id set!")

            rec.ensure_one()

            next_stage_in_progress = self.env['sale.subscription.stage'].search(
                [('category', '=', 'progress'), ('sequence', '>=', rec.stage_id.sequence)], limit=1)

            if not next_stage_in_progress:
                next_stage_in_progress = self.env['sale.subscription.stage'].search(
                    [('category', '=', 'progress')], limit=1)

            rec.stage_id = next_stage_in_progress

        return True

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            sub_template = self.env['sale.subscription.template'].browse(self.template_id.id)

            # Create a list for new lines
            new_lines = []

            # Separate tuition fee lines and other lines
            tuition_fee_lines = []
            other_fee_lines = []

            for i in sub_template.subs_lines:
                # Prepare the dictionary for the fee line
                subscription_line = {
                    'product_id': i.product_id.id,
                    'name': i.name,
                    'quantity': i.product_uom_qty,
                    'uom_id': 1,
                    'price_unit': i.price_unit,
                    'line_months_subscription_line': [(6, 0, i.line_months.ids)],
                }

                # Check if the product is a tuition fee
                if i.product_id.name.lower() == 'tuition fee':
                    tuition_fee_lines.append((0, 0, subscription_line))
                else:
                    other_fee_lines.append((0, 0, subscription_line))

            # Add discount lines separately to avoid overwriting
            # for line in self.recurring_invoice_line_ids:
            #     if line.product_id.is_discount_type:
            #         discount_line = {
            #             'product_id': line.product_id.id,
            #             'name': line.name,
            #             'uom_id': 1,
            #             'price_unit': line.price_unit,
            #         }
            #         other_fee_lines.append((0, 0, discount_line))

            # Clear old lines
            self.recurring_invoice_line_ids = False

            # Add the tuition fee first, followed by other lines
            self.recurring_invoice_line_ids = tuition_fee_lines + other_fee_lines

    def generate_invoice_cus(self):
        invoices = self.env['account.move']
        for rec in self:
            if rec.recurring_next_date:
                next_month = rec.recurring_next_date.strftime('%b')
                domain = [('product_id', '!=', False),
                          ('line_months_subscription_line.x_name', '=', next_month)]
                products = rec.mapped('recurring_invoice_line_ids').filtered_domain(domain).product_id
                invoice_lines = []
                total_recurring_fee = 0.0
                total_discount = 0.0

                # Calculate total recurring fee
                # for line in rec.recurring_invoice_line_ids:
                #     total_recurring_fee += line.price_unit

                # # Calculate total discount from student concessions
                # student_concessions = rec.partner_id.student_concessions
                # for concession in student_concessions:
                #     # Assuming concession has a field discount_percentage
                #     discount_percentage = concession.discount_value or 0.0
                #     total_discount += total_recurring_fee * (discount_percentage / 100)
                #
                # # Adjust total amount for discount
                # adjusted_total = total_recurring_fee - total_discount

                # Generate invoice lines
                for prod in products:
                    for line in rec.recurring_invoice_line_ids:
                        if line.product_id.id == prod.id:
                            invoice_lines.append((0, 0, {
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'quantity': 1,
                                'price_unit': line.price_unit,
                            }))

                # Add discount line to the invoice if discount is applied

                # if total_discount > 0:
                #     for concession in student_concessions:
                #         concession_product = self.env['product.product'].search(
                #             [('product_tmpl_id', '=', concession.product_id.id)], limit=1)
                #         discount_percentage = concession.discount_value or 0.0
                #         discount_price = total_recurring_fee * (discount_percentage / 100)
                #         invoice_lines.append((0, 0, {
                #             'product_id': concession_product.id,
                #             'name': concession_product.name,
                #             'quantity': 1,
                #             'price_unit': -discount_price,
                #         }))

                invoice_date_due = rec.recurring_next_date + timedelta(days=9)
                due_date_II = invoice_date_due + timedelta(days=7)
                invoice_vals = {
                    'partner_id': rec.partner_id.id,
                    'invoice_date': rec.recurring_next_date,
                    'move_type': 'out_invoice',
                    'journal_id': rec.x_studio_journal.id,
                    'invoice_line_ids': invoice_lines,
                    'invoice_ref': rec.id,
                    'due_date_II': due_date_II,
                    'invoice_date_due': invoice_date_due,
                    'branch_id': rec.partner_id.branch_id.id,
                    # 'amount_total': adjusted_total  # Set the adjusted total
                }
                invoice = rec.env['account.move'].sudo().create(invoice_vals)
                new_recurring_next_date = rec.recurring_next_date + relativedelta(months=1)
                rec.recurring_next_date = new_recurring_next_date
                invoices += invoice
        return invoices

    def _inherit_recurring_create_invoice(self, automatic=False):
        invoices = super(SaleSubscriptionInherit, self)._recurring_create_invoice(automatic=True, batch_size=20)
        for invoice in invoices:
            update_invoice = {
                'invoice_date': datetime.date.today(),
                'invoice_date_due': datetime.date.today() + timedelta(days=9),
                'branch_id': invoice.partner_id.branch_id.id,
                'amount_total': invoice.amount_total,
                'invoice_ref': invoice.id,
                'move_type': 'out_invoice',
            }
            invoice.write(update_invoice)
            # invoice.invoice_date = datetime.date.today()
            # invoice.invoice_date_due = invoice.invoice_date + timedelta(days=9)
            # invoice.due   _date_II =  invoice.recurring_next_date
            # invoice.invoice_ref = invoice.invoice_ref.id
            # invoice.branch_id = invoice.branch_id.id
            # invoice.amount_total = invoice.amount_total

    @api.model
    def _inherit_cron_recurring_create_invoice(self):
        return self._inherit_recurring_create_invoice(automatic=True)


class SaleSubscriptionLineInherit(models.Model):
    _inherit = 'sale.subscription.line'
    line_months_subscription_line = fields.Many2many(
        'x_billing_months', string='Months')

    @api.model
    def assign_months_to_all_fee_plans(self):
        # Retrieve all months
        all_months = self.env['x_billing_months'].search([('display_name', '!=', 'july')])

        # Check if months are available
        if not all_months:
            return

        # Retrieve all fee plans
        fee_plans = self.search([])

        # Assign all months to each fee plan line
        for fee_plan in fee_plans:
            fee_plan.line_months_subscription_line = [(6, 0, all_months.ids)]

# class ProductMonthLineInherit(models.Model):
#     _inherit = 'product.product'
#     month_product = fields.Many2many('billing.months', string='Months')
