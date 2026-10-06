# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SurveyProductLines(models.Model):
    _name = "survey.product.line"
    _description = "Survey Product Line"

    crm_lead_id = fields.Many2one("crm.lead")
    product_id = fields.Many2one("product.product")
    quantity = fields.Float()
    unit_price = fields.Float(related="product_id.lst_price")
    total_amount = fields.Float(
        compute="_fetch_amount_total", string="Line Total Amount"
    )

    @api.depends("quantity", "unit_price")
    def _fetch_amount_total(self):
        for rec in self:
            rec.total_amount = rec.quantity * rec.unit_price
