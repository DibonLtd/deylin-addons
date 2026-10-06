{
    'name': 'POS Pricelist Guard',
    'version': '17.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Block selling products at the POS unless they are explicitly '
               'priced in the active pricelist',
    'description': """
Prevents cashiers from adding a product to a POS order when the order's
pricelist has no price line naming that exact product (or one of its
variants). Category-wide and all-products formula rules do not count —
those are precisely the "default price" fallback this module exists to stop.

Refund flows are unaffected, and registers with no pricelist configured
are not restricted.
""",
    'author': 'Trinity Energy',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_pricelist_guard/static/src/js/pos_pricelist_guard.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
