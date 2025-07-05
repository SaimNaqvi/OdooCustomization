from odoo import models, api, fields, _
from odoo.exceptions import UserError
import json
import datetime


class InheritSaleSubscription(models.Model):
    _inherit = "sale.subscription"

    partner_id = fields.Many2one('res.partner', string='Student', domain=[('is_student', '=', True)])
    x_studio_facts_id = fields.Integer(related="partner_id.facts_id", string="Facts ID", store=True, readonly=True)
    x_studio_grade = fields.Selection(related="partner_id.current_grade_selection", string="Grade", store=True, readonly=True)
    x_studio_section = fields.Selection(related="partner_id.new_homeroom", string="Section", store=True, readonly=True)
    template_id = fields.Many2one(
        'sale.subscription.template', string='Fee Template',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True,
        help="The subscription template defines the invoice policy and the payment terms.", tracking=True,
        check_company=True)
    x_studio_billing_method = fields.Selection([('Monthly', 'Monthly'), ('Quarterly', 'Quarterly')], copy=True, store=True)
    x_studio_journal = fields.Many2one('account.journal', string="Journal", related="template_id.journal_id")
    x_studio_date_field_BupKl = fields.Date(string="New Date", store=True, copy=True)
    x_invoice_ref_account_move_count = fields.Integer(string="Invoice Ref count", compute='compute_invoice_count')
    student_code = fields.Char(string="Student Code", related='partner_id.student_code', copy=True, store=True)

    grade_section_display = fields.Char(string='Grade and Section', compute='_compute_grade_and_section_display',
                                        store=True)

    tuition_fee = fields.Float(string='Tuition Fee', compute='_compute_fees', inverse='_inverse_tuition_fee',
                               store=True)
    utility_fee = fields.Float(string='Utility Fee', compute='_compute_fees', inverse='_inverse_utility_fee',
                               store=True)
    development_fee = fields.Float(string='Development Fee', compute='_compute_fees',
                                   inverse='_inverse_development_fee', store=True)
    computer_fee = fields.Float(string='Computer Fee', compute='_compute_fees', inverse='_inverse_computer_fee',
                                store=True)

    @api.depends('recurring_invoice_line_ids')
    def _compute_fees(self):
        for subscription in self:
            subscription.tuition_fee = sum(line.price_unit for line in subscription.recurring_invoice_line_ids if
                                           line.product_id.name == 'Tuition Fee')
            subscription.utility_fee = sum(line.price_unit for line in subscription.recurring_invoice_line_ids if
                                           line.product_id.name == 'Utility Fee')
            subscription.development_fee = sum(line.price_unit for line in subscription.recurring_invoice_line_ids if
                                               line.product_id.name == 'Development Fee')
            subscription.computer_fee = sum(line.price_unit for line in subscription.recurring_invoice_line_ids if
                                            line.product_id.name == 'Computer Fee')

    def _inverse_tuition_fee(self):
        self._update_fee('Tuition Fee', self.tuition_fee)

    def _inverse_utility_fee(self):
        self._update_fee('Utility Fee', self.utility_fee)

    def _inverse_development_fee(self):
        self._update_fee('Development Fee', self.development_fee)

    def _inverse_computer_fee(self):
        self._update_fee('Computer Fee', self.computer_fee)

    def _update_fee(self, product_name, fee_value):
        for subscription in self:
            line = subscription.recurring_invoice_line_ids.filtered(lambda l: l.product_id.name == product_name)
            if line:
                line.price_unit = fee_value
            else:
                product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
                if product:
                    self.env['sale.subscription.line'].create({
                        'product_id': product.id,
                        'analytic_account_id': subscription.id,
                        'price_unit': fee_value,
                        'quantity': 1,
                        'uom_id': product.uom_id.id
                    })
    def _compute_grade_and_section_display(self):
        section_dict = dict(self.partner_id.fields_get(allfields=['new_homeroom'])['new_homeroom']['selection'])
        for partner in self.partner_id:
            if partner.current_grade_selection and partner.new_homeroom:
                capitalized_section = section_dict.get(partner.new_homeroom, '')
                partner.grade_section_display = f"Class {partner.current_grade_selection} {capitalized_section}"
            elif partner.current_grade_selection:
                partner.grade_section_display = f"Class {partner.current_grade_selection}"
            else:
                partner.grade_section_display = ''

    def compute_invoice_count(self):
        try:
            for record in self:
                record['x_invoice_ref_account_move_count'] = self.env['account.move'].search_count([('invoice_ref', '=', record.id)])
        except Exception as e:
            record['x_invoice_ref_account_move_count'] = 0

    def action_account_move(self):
        return {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('invoice_ref', '=', self.id)],
            'context': {'search_default_invoice_ref': self.id, 'default_invoice_ref': self.id}
        }
    def set_billing_method(self):
        all_fee_plans = self.env['sale.subscription'].search([])

    def action_open_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Subscription',
            'res_model': 'sale.subscription',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }



