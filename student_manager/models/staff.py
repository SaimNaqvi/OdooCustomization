from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    staff_title = fields.Char(string="Staff Title", store=True)
    department = fields.Char(string="Department")

    @api.model
    def default_get(self, fields_list):
        # Call the super method to get the default values
        defaults = super(ResPartner, self).default_get(fields_list)

        # Check if the context has 'is_staff_view' set to True
        is_staff_view = self._context.get('is_staff_view', False)
        if is_staff_view:
            # Try to get the 'Staff' title from the 'res.partner.title' model
            title = self.env['res.partner.title'].search([('name', '=', 'Staff')], limit=1)
            if title:
                # If the 'Staff' title is found, set it as the default title
                defaults['title'] = title.id  # Set the title field with the ID of 'Staff'


            else:
                # Handle case where the 'Staff' title is not found
                defaults['title'] = False

        return defaults
