# -*- coding: utf-8 -*-
{
    "name": "Pos Payment Reference",
    "summary": """ Pos Payment Reference """,
    "description": """
 Pos Payment Reference.
 """,
    "author": "Sybyl",
    "website": "https://sybyl.com",
    "category": "Sales/Point of Sale",
    "version": "17.0.0.0",
    "depends": [
        "point_of_sale"
    ],
    "data": [
        "views/payment_method.xml",
        "views/pos_order_view.xml",
        "views/account_move.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'sybyl_pos_payment_reference/static/src/js/**/*.js',
            'sybyl_pos_payment_reference/static/src/js/pos_screen.js',
            'sybyl_pos_payment_reference/static/src/xml/payment_lines.xml',
        ]
    },
    "application": True,
    "license": "LGPL-3",
}