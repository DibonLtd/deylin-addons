
from odoo import fields, models, api, tools, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_payment_ref = fields.Char("POS Payment Reference",compute="_fetch_payment_ref")
    show_payment_ref = fields.Boolean(default=False) 
    
    def _fetch_payment_ref(self):
        for rec in self:
            pos_order = self.env['pos.order'].sudo().search([('name','=',rec.invoice_origin)],limit=1)
            if pos_order:
                payment_references = pos_order.payment_ids.mapped('user_payment_reference')
                payment_references = [ref for ref in payment_references if ref]
                rec.pos_payment_ref = ', '.join(payment_references)
                rec.show_payment_ref = True
            else:
                rec.show_payment_ref = False
                rec.pos_payment_ref = ''