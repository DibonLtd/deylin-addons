# pylint: disable=E0401,C0114,C0115,C0116
from odoo import models

total_column = {}
sub_total_column = {}


class PosSessionXlsx(models.AbstractModel):
    _name = "report.sybyl_karura_pos.pos_session_xlsx"
    _description = "POS Session Xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, wizard):
        title = "POS Session Report"
        format0 = workbook.add_format(
            {"font_size": 12, "align": "vcenter", "bold": True, "font_name": "Arial"}
        )
        format1 = workbook.add_format(
            {
                "font_size": 10,
                "align": "vcenter",
                "bold": True,
                "font_name": "Arial",
                "bg_color": "ADD8E6",
            }
        )
        format2 = workbook.add_format(
            {"font_size": 10, "align": "vcenter", "font_name": "Arial"}
        )
        sheet = workbook.add_worksheet("pos_session_report")
        sheet.write(1, 1, title, format0)

        sheet.write(2, 1, "Session ID :", format1)
        sheet.write(2, 2, data.get("session_name"), format1)

        sheet.write(4, 0, "Sales", format0)
        sheet.write(5, 0, "Product Category", format1)
        sheet.write(5, 1, "Product", format1)
        sheet.write(5, 2, "Quantity", format1)
        sheet.write(5, 3, "Total (Tax excluded)", format1)

        sheet.set_column(0, 4, 20)

        i = 6
        total_qty = total_value = 0
        line_items_categ = data.get("line_items_categ")
        for category, details in line_items_categ.items():
            sheet.write(i, 0, category, format1)
            sheet.write(i, 1, "", format1)
            sheet.write(i, 2, details["total"][0], format1)
            total_qty += details["total"][0]
            sheet.write(i, 3, details["total"][1], format1)
            total_value += details["total"][1]
            for type_name, values in details["details"].items():
                i += 1
                sheet.write(i, 1, type_name, format2)
                sheet.write(i, 2, values[0], format2)
                sheet.write(i, 3, values[1], format2)
            i += 1
        i += 1
        sheet.write(i, 0, "Total", format1)
        sheet.write(i, 1, "", format1)
        sheet.write(i, 2, total_qty, format1)
        sheet.write(i, 3, total_value, format1)
        i += 3
        sheet.write(i, 0, "Taxes on sales", format0)
        i += 1
        sheet.write(i, 0, "Name", format1)
        sheet.write(i, 1, "Tax Amount", format1)
        sheet.write(i, 2, "Base Amount", format1)

        base_amount_total = tax_amount_total = 0
        line_items_tax = data.get("line_items_tax")

        for line_item_tax in line_items_tax:
            i += 1
            sheet.write(i, 0, line_item_tax, format2)
            line_items_tax.get(line_item_tax)
            sheet.write(i, 1, line_items_tax.get(line_item_tax)[0], format2)
            tax_amount_total += line_items_tax.get(line_item_tax)[0]
            sheet.write(i, 2, line_items_tax.get(line_item_tax)[1], format2)
            base_amount_total += line_items_tax.get(line_item_tax)[1]
        i += 1
        sheet.write(i, 0, "Total", format1)
        sheet.write(i, 1, tax_amount_total, format1)
        sheet.write(i, 2, base_amount_total, format1)
