from odoo import models, fields, api, _


class FkfpStaff(models.Model):
    _name = 'fkfp.staff'
    _description = 'Staff Information'
    _rec_name = 'staff_id'
    _order = 'staff_id asc'

    staff_id = fields.Char(string='Staff ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    name = fields.Char(string='Staff', store=True)
    phone = fields.Char(string='Phone', store=True)
    mobile = fields.Char(string='Mobile', store=True)
    father_name = fields.Char(string='Father/husband Name', store=True)
    province = fields.Char(string='Province', store=True)
    district = fields.Char(string='District', store=True)
    cnic = fields.Char(string='CNIC', store=True)
    village = fields.Char(string='village', store=True)
    nationality = fields.Selection(
        selection=[
            ('Afghan', 'Afghan'),
            ('Albanian', 'Albanian'),
            ('Algerian', 'Argentine'),
            ('Armenian', 'Armenian'),
            ('Australian', 'Australian'),
            ('Austrian', 'Austrian'),
            ('Azerbaijani', 'Azerbaijani'),
            ('Bangladeshi', 'Bangladeshi'),
            ('Belarusian', 'Belarusian'),
            ('Chinese', 'Chinese'),
            ('Colombian', 'Colombian'),
            ('Ethiopian', 'Ethiopian'),
            ('Indian', 'Indian'),
            ('Italian', 'Italian'),
            ('Pakistani', 'Pakistani'),
            ('Tajik', 'Tajik'),
        ],
        string='Nationality'
    )
    marital_status = fields.Selection(
        selection=[
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorced', 'Divorced'),
            ('widowed', 'Widowed'),
            ('separated', 'Separated'),
        ],
        string='Marital Status',
    )
    address = fields.Char(string='Address', store=True)
    country_id = fields.Many2one('res.country', string='Country', store=True)

    @api.model
    def create(self, vals):
        if vals.get('staff_id', _('New')) == _('New'):
            vals['staff_id'] = self.env['ir.sequence'].next_by_code('fkfp.staff') or _('New')
        return super(FkfpStaff, self).create(vals)

    def action_whatsapp(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'fkfp.whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_staff_id': self.id}, }
