from odoo import models, fields, api
from odoo.exceptions import UserError

CONCESSION_TYPES = [
    ('deserving case', 'Deserving Case'),
    ('discontinue', 'Discontinue'),
    ('donor', 'Donor'),
    ('employee child', 'Employee Child'),
    ('kinship', 'Kinship'),
    ('orphan', 'Orphan'),
    ('pastor child', 'Pastor child'),
    ('poor', 'Poor'),
    ('special case', 'Special Case'),
]


class StudentConcession(models.Model):
    _name = 'student.concession'
    _description = 'Student Concession'

    student_id = fields.Many2one('res.partner', string='Student')
    starting_date = fields.Date(string='Starting Date', store=True)
    concession_type = fields.Selection(CONCESSION_TYPES, string='Concession Type')
    concession_reason = fields.Text(string='Concession Reason')
    discount_percentage = fields.Float(string='Discount Percentage')

    product_id = fields.Many2one(
        'product.product',
        string='Charge on'
    )
    discount_type = fields.Selection([
        ('percentage', 'percentage'),
        ('fixed', 'fixed'),
    ], string='type')
    discount_value = fields.Float('Value')
    parent_product_id = fields.Many2one(comodel_name='product.product', string='parent product')
    parent_template_id = fields.Many2one(comodel_name='product.template', string='parent template')

    @api.onchange('discount_value', "discount_type")
    def _onchange_value(self):
        if self.discount_type == "percentage" and self.discount_value > 100:
            raise UserError("percentage cannot be larger then 100")

    @api.model
    def create(self, vals):
        result = super(StudentConcession, self).create(vals)
        result.update_existing_fee_plans()
        return result

    def write(self, vals):
        res = super(StudentConcession, self).write(vals)
        self.update_existing_fee_plans()
        return res

    def update_existing_fee_plans(self):
        for concession in self:
            student = concession.student_id
            if student:
                fee_plans = concession.env['sale.subscription'].search(
                    [('partner_id', '=', student.id), ('stage_id', '=', 'In Progress')])
                for fee_plan in fee_plans:
                    fee_plan.apply_concession()
