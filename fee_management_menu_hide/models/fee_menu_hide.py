from odoo import api, models, _

class AccountFollowupMenuHide(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def hide_customer_statements_menu(self):
        menu = self.env.ref('account_followup.customer_statements_menu')
        if menu:
            menu.active = False
    
    @api.model
    def hide_product_product_menu_sellable(self):
        menu = self.env.ref('account.product_product_menu_sellable')
        if menu:
            menu.active = False

    @api.model
    def hide_menu_account_customer(self):
        menu = self.env.ref('account.menu_account_customer')
        if menu:
            menu.active = False

# class FeeManagementMenuChange(models.Model):
#     _inherit = 'ir.ui.menu'

#     @api.model
#     def change_susbscription_menu_name(self):
#         menu = self.env.ref('sale_subscription.menu_sale_subscription')
#         if menu:
#             menu.name = 'Fee Plans'
