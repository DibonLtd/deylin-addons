/** @odoo-module */
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import { deserializeDateTime } from "@web/core/l10n/dates";

const { DateTime } = luxon;

/** Normalise a many2one value that may be `[id, name]` or a plain id. */
function m2oId(value) {
    return Array.isArray(value) ? value[0] : value;
}

/** A pricelist item is active when today falls inside its validity window. */
function itemIsActive(item) {
    const now = DateTime.now();
    try {
        if (item.date_start && deserializeDateTime(item.date_start) > now) {
            return false;
        }
        if (item.date_end && deserializeDateTime(item.date_end) < now) {
            return false;
        }
    } catch {
        // Unparseable dates: treat the item as active rather than block sales.
    }
    return true;
}

/**
 * True when the pricelist has a price line naming this exact product —
 * either its variant (product_id) or its template (product_tmpl_id).
 * Category-wide and all-products rules deliberately do NOT count: they are
 * the "default price" fallback this module exists to stop.
 */
function productListedInPricelist(product, pricelist) {
    const items =
        product.applicablePricelistItems?.[pricelist.id] ??
        pricelist.items ??
        [];
    return items.some((item) => {
        if (!itemIsActive(item)) {
            return false;
        }
        const variantId = m2oId(item.product_id);
        if (variantId) {
            return variantId === product.id;
        }
        const templateId = m2oId(item.product_tmpl_id);
        if (templateId) {
            return templateId === m2oId(product.product_tmpl_id);
        }
        return false;
    });
}

patch(PosStore.prototype, {
    /**
     * Block adding a product the active pricelist does not explicitly price.
     *
     * Notes:
     * - Registers without a pricelist are not restricted (nothing to check).
     * - Refunds are unaffected: the refund flow re-creates order lines
     *   directly and never passes through addProductToCurrentOrder, so items
     *   later removed from a pricelist can still be returned.
     */
    async addProductToCurrentOrder(product, options = {}) {
        const order = this.get_order();
        const pricelist = order?.pricelist;
        if (pricelist && !productListedInPricelist(product, pricelist)) {
            await this.popup.add(ErrorPopup, {
                title: _t("Product not in pricelist"),
                body: _t(
                    '"%s" is not in the pricelist "%s". It cannot be sold until it is added to that pricelist.',
                    product.display_name,
                    pricelist.display_name || pricelist.name
                ),
            });
            return;
        }
        return super.addProductToCurrentOrder(product, options);
    },
});
