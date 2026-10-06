/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
/**
 * @props partner
 */

patch(ActionpadWidget.prototype, {
    
    setup() {
        super.setup();
        this.data_refs = [];
        this.data_refs = this.load_data()
    },
    async load_data() {
        let result = await this.pos.get_all_ref()
        this.data_refs = result
        this.pos.references = result
        return result
    },
});

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.user_payment_reference = loadedData["pos.payment"];
        this.user_payment_reference = ''
        this.references = []
    },
    async check_ref_exist(code) {
        let res = await this.orm.call("pos.payment", "check_ref_exist", [null,{code}]);
        return res
    },
    async get_all_ref() {
        let res = await this.orm.call("pos.payment", "get_all_payment_ref", [[]]);
        return res
    },
});