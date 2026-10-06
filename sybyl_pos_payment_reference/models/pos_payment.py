# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Amaya Aravind (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields, models, api


class PosPayment(models.Model):
    """Class for inherited model pos payment
        Methods:
            get_payment_reference(self, order_list):
                Method to write payment reference to the corresponding order.
                Works through rpc call."""
    _inherit = 'pos.payment'

    user_payment_reference = fields.Char(string='Payment Reference',
                                         help='Payment reference entered by '
                                              'user.',default='')


    def check_ref_exist(self, code):
        if 'code' in code:
            is_exist = self.search([('user_payment_reference','=',code.get('code'))])
            if is_exist:
                return True
            else:
                return False
        return False

    def get_all_payment_ref(self):
        self._cr.execute("select user_payment_reference from pos_payment where user_payment_reference NOTNULL AND user_payment_reference!='';")
        data = self._cr.fetchall()
        user_payment_references = [item[0] for item in data]
        return user_payment_references

class PosOrder(models.Model):

    _inherit = 'pos.order'

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        fields = super()._payment_fields(order, ui_paymentline)
        fields.update({
                'user_payment_reference': ui_paymentline.get('user_payment_reference') or '',
            })
        return fields
