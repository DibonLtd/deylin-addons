# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    pos_receipt_title = fields.Text(string="POS Receipt Title")
    has_admin_rights = fields.Boolean(compute="_compute_admin_rights", default=False)

    def _compute_admin_rights(self):
        for rec in self:
            if rec.env.user.has_group(
                "point_of_sale.group_pos_user"
            ) or rec.env.user.has_group("point_of_sale.group_pos_manager"):
                rec.has_admin_rights = True
            else:
                rec.has_admin_rights = False
