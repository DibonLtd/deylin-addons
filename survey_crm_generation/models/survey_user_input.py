# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from datetime import timedelta


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    opportunity_id = fields.Many2one(comodel_name="crm.lead")

    def _prepare_opportunity(self):
        return {
            "name": self.survey_id.title,
            "tag_ids": [(6, 0, self.survey_id.crm_tag_ids.ids)],
            "partner_id": self.partner_id.id,
            "user_id": self.survey_id.crm_team_id.user_id.id,
            "team_id": self.survey_id.crm_team_id.id,
            "company_id": self.create_uid.company_id.id,
            "survey_user_input_id": self.id,
            "description": self._prepare_lead_description(),
            "survey_product_line_ids": self._prepare_product_vals()
        }

    def _prepare_product_vals(self):
        product_qty_input_lines = self.user_input_line_ids.filtered(
            lambda x: not x.skipped and x.value_quantity
        )
        vals_list = []
        for rec in product_qty_input_lines:
            if rec.value_quantity and rec.value_product_id:
                vals_list.append(
                    {
                        "product_id": rec.suggested_answer_id.product_id.id,
                        "quantity": rec.value_quantity,
                        "unit_price": rec.value_product_id.id,
                    }
                )
        if vals_list:
            return [(0, 0, record) for record in vals_list]
        else:
            return vals_list

    def _prepare_lead_description(self):
        """We can have surveys without partner. It's handy to have some relevant info
        in the description although the answers are linked themselves.

        :return str: description for the lead
        """
        relevant_answers = self.user_input_line_ids.filtered(
            lambda x: not x.skipped and x.question_id.show_in_lead_description
        )

        answer_dict = {}

        for answer in relevant_answers:
            question_title = answer.question_id.title

            if answer.answer_type == "suggestion":
                answer_value = answer.suggested_answer_id
            else:
                answer_value = answer[f'value_{answer.answer_type}']

            # Handle value Models
            if isinstance(answer_value, models.Model):
                # Case of Multi Models
                if len(answer_value._ids) > 1:
                    answer_text = '<ul>'
                    for answer_value_object in answer_value:
                        answer_text += f'<li>{answer_value_object.display_name}</li>'
                    answer_text += '</ul>'
                else:
                    # Remove duplicate title from display name
                    clean_display_name = answer_value.display_name.replace(question_title + ' : ', '')
                    answer_text = clean_display_name
            else:
                # Remove duplicate title from string value
                clean_value = str(answer_value).replace(question_title + ' : ', '')
                answer_text = clean_value

            if question_title in answer_dict:
                answer_dict[question_title] += f", {answer_text}"
            else:
                answer_dict[question_title] = answer_text

        li = ''.join(f'<li>{title}: {answers}</li>' for title, answers in answer_dict.items())

        description = f'<u>{_("Survey answers: ")}</u><ul>{li}</ul>'
        return description

    def _create_opportunity_post_process(self):
        """After creating the lead send an internal message with the input link"""
        self.opportunity_id.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": self.opportunity_id, "origin": self},
            subtype_xmlid='mail.mt_note',
        )

    def _mark_done(self):
        """Generate the opportunity when the survey is submitted"""
        res = super()._mark_done()
        if not self.survey_id.generate_leads:
            return res
        vals = self._prepare_opportunity()
        self.opportunity_id = self.env["crm.lead"].sudo().create(vals)
        self.opportunity_id.sudo().write({'date_deadline': self.opportunity_id.create_date + timedelta(days=15),
                                          'expected_revenue': self.opportunity_id.total_amount})
        relevant_documents_input = self.user_input_line_ids.filtered(
            lambda x: x.question_id.question_type == 'file'
        )
        if relevant_documents_input:
            if relevant_documents_input.attachment_ids:
                [rec.sudo().write({'res_id': self.opportunity_id.id,'res_model':self.opportunity_id._name}) for rec in relevant_documents_input.attachment_ids]
        self.opportunity_id.sudo().write({'date_deadline': self.opportunity_id.create_date + timedelta(days=15),
                                          'expected_revenue': self.opportunity_id.total_amount})
        self._create_opportunity_post_process()
        return res
