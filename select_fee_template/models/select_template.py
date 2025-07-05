from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError
import re


class SelectSubscriptionTemplateWizard(models.TransientModel):
    _name = 'select.subscription.template.wizard'

    template_id = fields.Many2one('sale.subscription.template', string='Subscription Template', required=True)
    branch_id = fields.Many2one('res.branch', string='Branch', readonly=True)
    student_ids = fields.Many2many('res.partner', string='Students')

    @api.model
    def default_get(self, fields):
        res = super(SelectSubscriptionTemplateWizard, self).default_get(fields)
        if 'default_branch_id' in self.env.context:
            res['student_ids'] = self.env.context.get('active_ids', [])
            res['branch_id'] = self.env.context.get('default_branch_id')
        return res

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            branch_name = self._get_branch_name(self.branch_id.name)
            return {'domain': {'template_id': [('name', 'ilike', branch_name)]}}
        return {'domain': {'template_id': []}}

    def _get_branch_name(self, branch_name):
        clean_branch_name = re.sub(r"\s*\(\d+\)$", "", branch_name)
        result = clean_branch_name.split('-')[0].strip() if '-' in clean_branch_name else clean_branch_name.strip()
        return result

    # @api.multi
    def button_confirm(self):
        for student in self.student_ids:
            existing_subscription = self.env['sale.subscription'].search([
                ('partner_id', '=', student.id),
            ])

            if existing_subscription.filtered(lambda sub: sub.stage_id.id != 3):
                raise UserError(
                    f"Cannot create a new subscription. Student '{student.name}' already has an open subscription."
                )

            # Create new subscription
            new_subscription = self.env['sale.subscription'].create({
                'x_studio_facts_id': student.facts_id,
                'partner_id': student.id,
                'date_start': fields.Date.today(),
                'template_id': self.template_id.id,
                'branch_id': student.branch_id.id,
            })

            # Add template lines
            for template_line in self.template_id.subs_lines:
                subscription_line = self.env['sale.subscription.line'].create({
                    'product_id': template_line.product_id.id,
                    'name': template_line.name,
                    'quantity': template_line.product_uom_qty,
                    'uom_id': 1,  # or template_line.product_id.uom_id.id
                    'price_unit': template_line.price_unit,
                    'line_months_subscription_line': [(6, 0, template_line.line_months.ids)],
                })
                new_subscription.recurring_invoice_line_ids |= subscription_line

            # Add concession lines
            for concession in student.student_concessions:
                concession_product = self.env['product.product'].search([
                    ('product_tmpl_id', '=', concession.product_id.id)
                ], limit=1)

                if concession_product:
                    concession_line = self.env['sale.subscription.line'].create({
                        'product_id': concession_product.id,
                        'name': concession_product.name,
                        'quantity': 1,
                        'uom_id': concession_product.uom_id.id,
                        'price_unit': 0,
                        'line_months_subscription_line': [(6, 0, [])],
                    })
                    new_subscription.recurring_invoice_line_ids |= concession_line

        return {'type': 'ir.actions.act_window_close'}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def button_open_fee_template_wizard(self):
        self.ensure_one()
        return {
            'name': 'Select Subscription Template',
            'type': 'ir.actions.act_window',
            'res_model': 'select.subscription.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_branch_id': self.branch_id.id},
        }

# class IrActions(models.Model):
#     _inherit = 'res.partner'

#     # action_type = fields.Selection(selection_add=[('open_template_selection_wizard', 'Open Fee Template Selection Wizard')])

#     def _open_template_selection_wizard(self):
#         return {
#             'name': 'Select Subscription Template',
#             'type': 'ir.actions.act_window',
#             'res_model': 'select.subscription.template.wizard',
#             'view_mode': 'form',
#             # 'view_id': self.env.ref('select_fee_template.view_select_subscription_template_wizard_form').id,
#             'target': 'new',
#         }
