# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo import fields, models, api, _
from datetime import datetime


class CrmLead(models.Model):
    _inherit = "crm.lead"

    survey_user_input_id = fields.Many2one(comodel_name="survey.user_input")
    survey_product_line_ids = fields.One2many(
        "survey.product.line", "crm_lead_id", string="Line Items"
    )
    is_approved = fields.Boolean(default=False,compute="_fetch_status")
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount")
    family_pass_details_ids = fields.One2many(
        "family.pass.details", "crm_lead_id", string="Family Pass Details"
    )
    subscribe_test = fields.Boolean(default=False)

    def action_set_won_rainbowman(self):
        self.ensure_one()
        if len(self.family_pass_details_ids) > 3:
            raise ValidationError(_("You can only add a maximum of 3 family pass details."))
        if len(self.family_pass_details_ids.filtered(lambda l:l.age >= 12)) > 1:
            raise ValidationError(_("You can only add 1 record with age 12 or older."))
        response = super().action_set_won_rainbowman()
        for rec in self.family_pass_details_ids:
            self.env['res.partner'].sudo().create({
                'name':rec.full_name,
                'parent_id':self.partner_id.id,
                'email': rec.email,
                'mobile':rec.mobile,
                'relation_contact':rec.relation_family,
                'date_of_birth':rec.date_of_birth
                })
        self.subscribe_test = True
        return response

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        for rec in self:
            if rec.stage_id.name == 'Subscribed':
                if len(rec.family_pass_details_ids) > 3:
                    raise ValidationError(_("You can only add a maximum of 3 family pass details."))
                if len(rec.family_pass_details_ids.filtered(lambda l:l.age >= 12)) > 1:
                    raise ValidationError(_("You can only add 1 record with age 12 or older."))
                response = super().action_set_won_rainbowman()
                for record in rec.family_pass_details_ids:
                    self.env['res.partner'].sudo().create({
                        'name':record.full_name,
                        'parent_id':rec.partner_id.id,
                        'email': record.email,
                        'mobile':record.mobile,
                        'relation_contact':record.relation_family,
                        'date_of_birth':record.date_of_birth
                        })
                rec.subscribe_test = True


    def _fetch_status(self):
        for rec in self:
            if rec.stage_id.name in ("Approved", "approve", "Approve"):
                rec.is_approved = True
            else:
                rec.is_approved = False

    @api.depends("survey_product_line_ids.total_amount")
    def _compute_total_amount(self):
        for lead in self:
            lead.total_amount = sum(
                line.total_amount for line in lead.survey_product_line_ids
            )

    def action_approve_crm(self):
        self.ensure_one()
        approve_stage_exists = (
            self.env["crm.stage"]
            .sudo()
            .search([("name", "in", ("Approved", "approve", "Approve"))], limit=1)
        )
        if not approve_stage_exists:
            raise ValidationError(
                _(
                    "CRM stage approve not exist.Please create stage which having name with Approved"
                )
            )
        mail_template_id = (
            self.env["mail.template"]
            .sudo()
            .search(
                [("name", "ilike", "Application Approved"), ("model", "=", "crm.lead")],
                limit=1,
            )
        )
        if not mail_template_id:
            mail_template_id = self.env.ref(
                "survey_crm_generation.mail_template_crm_approval"
            )
        mail_template_id.send_mail(self.id, force_send=True)
        self.write({"stage_id": approve_stage_exists.id, "is_approved": True})

    def action_sale_quotations_new(self):
        if self.survey_user_input_id:
            self.action_new_quotation_karura()
        else:
            return super(CrmLead, self).action_sale_quotations_new()


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


class FamilyPassDetails(models.Model):
    _name = "family.pass.details"
    _description = "Family Pass Details"

    crm_lead_id = fields.Many2one("crm.lead")
    full_name = fields.Char("Full Name",required=True)
    relation_family = fields.Selection(
        selection=[
            ('spouse', 'Spouse'),
            ('son', 'Son'),
            ('daughter', 'Daughter'),
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('in_law', 'In Law'),
            ('brother', 'Brother'),
            ('sister', 'Sister'),
            ('cousin', 'Cousin'),
            ('nephew', 'Nephew'),
            ('uncle', 'Uncle'),
            ('aunt', 'Aunt'),
            ('grand_parent', 'Grand Parent'),
        ],
        string="Relation",
        required=True,
    )
    date_of_birth = fields.Date(string="Date of Birth",required=True)
    email = fields.Char("Email",required=True)
    mobile = fields.Char("Mobile",required=True)
    age = fields.Integer("Age",compute="_compute_age")

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                birth_date = fields.Date.from_string(record.date_of_birth)
                today = datetime.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                record.age = age
            else:
                record.age = 0
