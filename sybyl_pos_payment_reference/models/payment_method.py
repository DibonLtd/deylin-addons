
from odoo import fields, models, api, tools, _


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    enable_payment_ref = fields.Boolean(string="Enable Payment Ref")
    
    user_payment_reference = fields.Char(string='Payment Reference',
                                         help='Payment reference entered by '
                                              'user.',default='')