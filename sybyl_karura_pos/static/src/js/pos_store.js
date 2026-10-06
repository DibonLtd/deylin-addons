/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    redirectToBackend() {
        const result = super.redirectToBackend(...arguments);
        this.reset_cashier();
        return result;
    },
});