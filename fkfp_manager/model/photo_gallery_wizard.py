from odoo import models, fields, api


class PhotoGalleryWizard(models.TransientModel):
    _name = 'photo.gallery.wizard'
    _description = 'Photo Gallery Wizard'

    # Define fields for the wizard model
    partner_id = fields.Many2one('res.partner', string='Student')

    before_home_ids = fields.One2many('photo.gallery.line', 'wizard_id_before', string='Before Home Photos')
    followup_home_ids = fields.One2many('photo.gallery.line', 'wizard_id_followup', string='Follow-up Photos')
    after_complete_ids = fields.One2many('photo.gallery.line', 'wizard_id_after', string='After Complete Photos')

    @api.model
    def default_get(self, fields_list):
        res = super(PhotoGalleryWizard, self).default_get(fields_list)

        # Preload saved images based on partner_id when wizard is opened
        partner = self.env.context.get('active_id')  # Get the current partner ID
        if partner:
            partner_obj = self.env['res.partner'].browse(partner)
            # Fetch images for before_home_ids, followup_home_ids, after_complete_ids
            res.update({
                'before_home_ids': [
                    (6, 0, partner_obj.photo_gallery_ids.filtered(lambda l: l.image_type == 'before').ids)],
                'followup_home_ids': [
                    (6, 0, partner_obj.photo_gallery_ids.filtered(lambda l: l.image_type == 'followup').ids)],
                'after_complete_ids': [
                    (6, 0, partner_obj.photo_gallery_ids.filtered(lambda l: l.image_type == 'after').ids)],
            })
        return res

    def action_save(self):
        for record in self:
            # Save images and associate them with the partner_id
            for line in record.before_home_ids:
                if line.image:
                    line.partner_id = record.partner_id
                    line.image_name = line.image_name or "Before Home Image {}".format(line.id)  # Set the image name
                    line.image_type = 'before'  # Mark this image as 'Before'

            for line in record.followup_home_ids:
                if line.image:
                    line.partner_id = record.partner_id
                    line.image_name = line.image_name or "Follow-up Image {}".format(line.id)  # Set the image name
                    line.image_type = 'followup'  # Mark this image as 'Follow-up'

            for line in record.after_complete_ids:
                if line.image:
                    line.partner_id = record.partner_id
                    line.image_name = line.image_name or "After Complete Image {}".format(line.id)  # Set the image name
                    line.image_type = 'after'  # Mark this image as 'After'

        # Redirect to a new window to show the saved images
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Photo Gallery',
            'res_model': 'photo.gallery.line',
            'view_mode': 'tree,form',  # Use tree (list) or form view
            'domain': [('partner_id', '=', record.partner_id.id)],  # Filter by partner_id
            'target': 'current',  # Open in the same window
        }


class PhotoGalleryLine(models.TransientModel):
    _name = 'photo.gallery.line'
    _description = 'Photo Gallery Line'

    image = fields.Binary('Photo')

    # Define Many2one relationships for the Wizard
    wizard_id_before = fields.Many2one('photo.gallery.wizard', string="Before Home", ondelete='cascade')
    wizard_id_followup = fields.Many2one('photo.gallery.wizard', string="Follow-up", ondelete='cascade')
    wizard_id_after = fields.Many2one('photo.gallery.wizard', string="After Complete", ondelete='cascade')

    # Ensure partner_id exists here if it's required in this model
    partner_id = fields.Many2one('res.partner', string="Student")
    image_name = fields.Char('Image Name')  # Store the name of the image
    image_type = fields.Selection([
        ('before', 'Before'),
        ('followup', 'Follow-up'),
        ('after', 'After Complete')
    ], string='Image Type')  # Store the type of the image


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Add reverse One2many relationship for partner_id
    photo_gallery_ids = fields.One2many('photo.gallery.line', 'partner_id', string='Photo Gallery')
