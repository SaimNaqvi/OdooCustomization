from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    father_name = fields.Char(string='Father/husband Name')
    province = fields.Char(string='Province')
    district = fields.Char(string='District')
    tehsil = fields.Char(string='Tehsil')
    uc = fields.Char(string='UC')  # Define the new field
    cnic = fields.Char(string='CNIC', store=True)
    village = fields.Char(string='village')
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
    status_id = fields.Many2one('project.status', string='Status', ondelete='set null')
    num_school_children = fields.Integer(string='No of School Going Children')
    num_of_dependent = fields.Integer(string='no of dependent')
    beneficiary_id = fields.Integer(string="System ID", readonly=True, store=True)
    user_define_code = fields.Integer(string='UDC', store=True)
    cost_amount = fields.Integer(string='Cost Amount', store=True)

    full_address = fields.Char(string='Street', store=True)

    donor_ids = fields.Many2many('fkfp.donor', 'fkfp_donor_beneficiary_rel', 'beneficiary_id', 'donor_id',
                                 string='Donors')
    donor_line_ids = fields.One2many('fkfp.donor.line', 'beneficiary_id', string='Donors')

    photo_gallery_ids = fields.One2many('fkfp.photo.gallery', 'partner_id', string='Photo Gallery')
    document_ids = fields.One2many('fkfp.partner.document', 'partner_id', string='Documents')

    @api.onchange('cnic')
    def _onchange_format_cnic(self):
        for rec in self:
            if rec.cnic and rec.cnic.isdigit() and len(rec.cnic) == 13:
                rec.cnic = f"{rec.cnic[:5]}-{rec.cnic[5:12]}-{rec.cnic[12]}"

    @api.model
    def create(self, vals):
        # Auto-increment Beneficiary ID if not set
        if 'beneficiary_id' not in vals or not vals.get('beneficiary_id'):
            max_id = self.env['res.partner'].sudo().search(
                [('beneficiary_id', '!=', False)],
                order='beneficiary_id desc',
                limit=1
            ).beneficiary_id
            vals['beneficiary_id'] = max_id + 1 if max_id else 1

        # Create partner
        partner = super(ResPartner, self).create(vals)

        # Send WhatsApp Notification
        try:
            self.env['whatsapp.meta.service'].send_director_notification(partner)
        except Exception as e:
            _logger.warning("WhatsApp notification failed: %s", str(e))

        return partner

        # # Fields to watch
        # fields_to_check = {'status_id', 'cnic', 'mobile'}
        # triggering_fields = fields_to_check.intersection(vals.keys())
        #
        # # Save old values if needed in message (optional)
        # result = super(ResPartner, self).write(vals)
        #
        # # Send update notification only if specific fields changed
        # if triggering_fields:
        #     try:
        #         self.env['whatsapp.meta.service'].send_director_notification(self, action='update', changed_fields=triggering_fields)
        #     except Exception as e:
        #         _logger.warning("Update notification failed: %s", str(e))

    def write(self, vals):
        old_status = self.status_id.status_name
        old_address = self.street
        old_mobile = self.mobile

        result = super(ResPartner, self).write(vals)

        if 'status_id' in vals:
            new_status = self.status_id.status_name
            try:
                self.env['whatsapp.meta.service'].send_director_notification_update(
                    partner=self,
                    action='update',
                    changed_fields=['status_id'],
                    old_value=old_status,
                    new_value=new_status
                )
                self.message_post(
                    body=f"🔁 Status changed from {old_status} ➜ <b>{new_status}</b>."
                )
            except Exception as e:
                raise UserError(_("Update notification failed: %s") % str(e))

        elif 'mobile' in vals:
            new_mobile = self.mobile
            try:
                self.env['whatsapp.meta.service'].send_director_notification_update(
                    partner=self,
                    action='update',
                    changed_fields=['mobile'],
                    old_value=old_mobile,
                    new_value=new_mobile
                )
                self.message_post(
                    body=f"🔁 Status changed from {old_mobile} ➜ <b>{new_mobile}</b>."
                )
            except Exception as e:
                raise UserError(_("Update notification failed: %s") % str(e))

        elif 'street' in vals:  # Fixing incorrect 'address' field key
            new_address = self.street
            try:
                self.env['whatsapp.meta.service'].send_director_notification_update(
                    partner=self,
                    action='update',
                    changed_fields=['address'],
                    old_value=old_address,
                    new_value=new_address
                )
                self.message_post(
                    body=f"🔁 Address changed from {old_address} ➜ {new_address}."
                )
            except Exception as e:
                raise UserError(_("Update notification failed: %s") % str(e))

        return result

    @api.model
    def default_get(self, fields_list):
        res = super(ResPartner, self).default_get(fields_list)
        company = self.env['res.company'].search([('name', '=', 'FKFP')], limit=1)
        if company:
            res['company_id'] = company.id
        return res

    def action_open_partner_documents(self):
        self.ensure_one()
        return {
            'name': 'Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'fkfp.partner.document',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
            },
            'target': 'current',
        }

    def action_partner_photo_gallery(self):
        self.ensure_one()
        return {
            'name': 'Photo Gallery',
            'type': 'ir.actions.act_window',
            'res_model': 'fkfp.photo.gallery',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
            },
            'target': 'current',
        }

    def action_print_documents(self):
        self.ensure_one()
        return {
            'name': 'Print',
            'type': 'ir.actions.act_window',
            'res_model': 'fkfp.print',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
            },
            'target': 'current',
        }

    @api.depends('cnic')
    def _compute_cnic(self):
        for record in self:
            if record.cnic:
                # Format the CNIC to include dashes
                record.cnic = self.format_cnic(record.cnic)

    def format_cnic(self, cnic):
        # Assuming CNIC is 13 digits long
        if len(cnic) == 13:
            return f"{cnic[:5]}-{cnic[5:12]}-{cnic[12]}"
        return cnic

    @api.model
    def action_open_donor(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fkfp_manager.donor',
            'view_mode': 'form',
            'view_id': self.env.ref('fkfp_manager.view_donor_form').id,
            'target': 'current',
        }

    @api.model
    def action_open_photo_gallery(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fkfp_manager.photo_gallery',
            'view_mode': 'form',
            'view_id': self.env.ref('fkfp_manager.view_photo_gallery_form').id,
            'target': 'current',
        }

    def action_open_photo_gallery(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Photo Gallery',
            'res_model': 'photo.gallery.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
            },
        }

    def auto_assign_beneficiary_id(self):
        for record in self:
            pass

    def action_print_cv_report(self):
        return self.env.ref('fkfp_manager.action_report_print_pdf').report_action(self)


class FkfpDonorLine(models.Model):
    _name = 'fkfp.donor.line'
    _description = 'Donor Line (Donor-Beneficiary Relation)'

    donor_id = fields.Many2one('fkfp.donor', string='Donor', required=True, ondelete='cascade')
    beneficiary_id = fields.Many2one('res.partner', string='Beneficiary', required=True, ondelete='cascade',
                                     readonly=True)
    amount_used = fields.Float(string='Amount Used')
