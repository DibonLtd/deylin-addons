/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

patch(Order.prototype, {
    async pay() {
        if (!this.canPay()) {
            return;
        }
        const zeroQuantityProducts = this.orderlines.filter(
            (line) => line.quantity === 0
        ).map(
            (line) => line.get_product().display_name
        );
        if (zeroQuantityProducts.length > 0) {
            const zeroQuantityProductsString = zeroQuantityProducts.join(', ');
            const message = `${zeroQuantityProductsString} not allowed with 0 quantity`;
            this.env.services.popup.add(ErrorPopup, {
                title: _t("Zero Quantity Products"),
                body: _t(message),
            });
            return;
        }

        if (
            this.orderlines.some(
                (line) => line.get_product().tracking !== "none" && !line.has_valid_product_lot()
            ) &&
            (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)
        ) {
            const { confirmed } = await this.env.services.popup.add(ConfirmPopup, {
                title: _t("Some Serial/Lot Numbers are missing"),
                body: _t(
                    "You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?"
                ),
                confirmText: _t("Yes"),
                cancelText: _t("No"),
            });
            if (confirmed) {
                this.pos.mobile_pane = "right";
                this.env.services.pos.showScreen("PaymentScreen");
            }
        } else {
            this.pos.mobile_pane = "right";
            this.env.services.pos.showScreen("PaymentScreen");
        }
    }
});