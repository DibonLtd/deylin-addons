# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError

from odoo import models, fields


class PosSession(models.Model):
    _inherit = "pos.session"

    has_closing_rights = fields.Boolean(compute="_compute_closing_rights")

    def _compute_closing_rights(self):
        for rec in self:
            if rec.user_id.id == self.env.user.id or self.env.user.has_group(
                "point_of_sale.group_pos_manager"
            ):
                rec.has_closing_rights = True
            else:
                rec.has_closing_rights = False

    def _loader_params_pos_session(self):
        result = super()._loader_params_pos_session()
        result["search_params"]["fields"].extend(["has_closing_rights"])
        return result

    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()
        result["search_params"]["fields"].extend(
            ["pos_receipt_title", "has_admin_rights"]
        )
        return result

    def cron_pos_session_closing_control(self):
        sessions = self.search([("state", "in", ["opening_control", "opened"])])
        for session in sessions:
            try:
                session.action_pos_session_closing_control()
                session.action_pos_session_close()
            except (UserError, ValidationError):
                pass
