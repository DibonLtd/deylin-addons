# -*- coding: utf-8 -*-
{
    "name": "Sybyl Karura POS Extended",
    "summary": """ Sybyl Karura POS Extended.""",
    "author": "Sybyl",
    "website": "https://sybyl.com",
    "category": "Sales/Point of Sale",
    "version": "17.0.0.0",
    "depends": [
        "point_of_sale",
        "pos_hr",
        "report_xlsx",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/point_of_sale_report.xml",
        "views/res_company_view.xml",
        "views/pos_session_view.xml",
        "wizard/pos_daily_sales_reports.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "sybyl_karura_pos/static/src/js/pos_receipt_changes.js",
            "sybyl_karura_pos/static/src/js/pos_store.js",
            "sybyl_karura_pos/static/src/js/pos_zero_quantity_restriction.js",
            "sybyl_karura_pos/static/src/xml/pos_receipt_extended.xml",
            "sybyl_karura_pos/static/src/xml/session_closing_popup.xml",
        ]
    },
    "application": True,
    "license": "LGPL-3",
}
