# -*- coding: utf-8 -*-

import datetime

import pytz

from odoo import fields, models


class PosDetails(models.TransientModel):
    _inherit = "pos.details.wizard"

    def _default_start_date(self):
        result = super(PosDetails, self)._default_start_date()
        user_tz = self.env.context.get("tz") or self.env.user.tz or "UTC"
        local_tz = pytz.timezone(user_tz)

        if isinstance(result, str):
            result = fields.Datetime.from_string(result)
        result = local_tz.localize(
            result.replace(hour=0, minute=0, second=0, microsecond=0), is_dst=None
        )
        utc_datetime = result.astimezone(pytz.utc).replace(tzinfo=None)
        return utc_datetime

    start_date = fields.Datetime(default=_default_start_date)

    def _default_end_date(self):
        end_date = datetime.datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=00
        )
        user_tz = self.env.context.get("tz") or self.env.user.tz or "UTC"
        local_tz = pytz.timezone(user_tz)

        if isinstance(end_date, str):
            end_date = fields.Datetime.from_string(end_date)
        end_date = local_tz.localize(
            end_date.replace(hour=23, minute=59, second=59, microsecond=00), is_dst=None
        )
        utc_datetime = end_date.astimezone(pytz.utc).replace(tzinfo=None)
        return utc_datetime

    end_date = fields.Datetime(default=_default_end_date)


class PosDailyReport(models.TransientModel):
    _inherit = "pos.daily.sales.reports.wizard"

    def get_xlsx_report(self):
        line_items_categ = {}
        for categ_id in self.pos_session_id.order_ids.lines.product_id.categ_id:
            line_product_ids = self.pos_session_id.order_ids.lines.product_id.filtered(
                lambda l: l.categ_id.id == categ_id.id
            )
            line_total = self.pos_session_id.order_ids.lines.filtered(
                lambda l: l.product_id.categ_id.id == categ_id.id
            )
            line_items_categ[categ_id.name] = {
                "total": [
                    sum(line_total.mapped("qty")),
                    sum(line_total.mapped("price_subtotal")),
                ],
                "details": {},
            }
            for line_product_id in line_product_ids:
                lines = self.pos_session_id.order_ids.lines.filtered(
                    lambda l: l.product_id.categ_id.id == categ_id.id
                    and l.product_id.id == line_product_id.id
                )
                line_items_categ[categ_id.name]["details"].update(
                    {
                        line_product_id.name: [
                            sum(lines.mapped("qty")),
                            sum(lines.mapped("price_subtotal")),
                        ]
                    }
                )
        line_items_tax = {}
        tax_ids = self.pos_session_id.order_ids.lines.tax_ids
        for tax_id in tax_ids:
            sample_ids = self.pos_session_id.order_ids.lines.filtered(
                lambda l: l.tax_ids.id == tax_id.id
            )
            line_items_tax[tax_id.name] = [
                sum(sample_ids.mapped("price_subtotal_incl"))
                - sum(sample_ids.mapped("price_subtotal")),
                sum(sample_ids.mapped("price_subtotal")),
            ]
        data = {
            "config_ids": self.pos_session_id.config_id.ids,
            "session_ids": self.pos_session_id.ids,
            "session_name": self.pos_session_id.name,
            "line_items_categ": line_items_categ,
            "line_items_tax": line_items_tax,
        }
        return self.env.ref("sybyl_karura_pos.sale_details_xlsx_report").report_action(
            [], data=data
        )
