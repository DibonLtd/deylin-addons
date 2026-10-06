from odoo import fields, models, api, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.onchange('company_id')
    def _onchange_company_id_warning(self):
        self.show_update_pricelist = True
        if 'is_from_lead' in self.env.context:
            is_from_lead = True
        else:
            is_from_lead = False

        if self.order_line and self.state == 'draft' and not is_from_lead:
            return {
                'warning': {
                    'title': _("Warning for the change of your quotation's company"),
                    'message': _("Changing the company of an existing quotation might need some "
                                 "manual adjustments in the details of the lines. You might "
                                 "consider updating the prices."),
                }
            }