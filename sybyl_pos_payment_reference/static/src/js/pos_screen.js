/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { PaymentScreenPaymentLines } from "@point_of_sale/app/screens/payment_screen/payment_lines/payment_lines";
import { _t } from "@web/core/l10n/translation";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
let order_list = []
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConnectionLostError } from "@web/core/network/rpc_service";



import { Payment } from "@point_of_sale/app/store/models";

patch(PaymentScreen.prototype, {
    async _finalizeValidation() {
        const order = this.pos.get_order();
        let allContainUserPaymentReference = true;
        if(order.paymentlines.length){
            for (let i = 0; i < order.paymentlines.length; i++) {
                if (!order.paymentlines[i].hasOwnProperty('user_payment_reference') && order.paymentlines[i].payment_method.enable_payment_ref) {
                    allContainUserPaymentReference = false;
                    this.popup.add(ErrorPopup, {
                        title: _t("Missing Payment Reference"),
                        body: _t("Check Payment Lines to add Payment reference."),
                    });
                    return false
                }
            }
        }
        if(allContainUserPaymentReference){
            await super._finalizeValidation(...arguments);
        }
   }
});

patch(PaymentScreenPaymentLines.prototype, {
    async IsPaymentReferenceButton(paymentline) {
        var place_holder = _t('eg:PREF16')
        if (paymentline.user_payment_reference != undefined){
            if (paymentline.user_payment_reference.length > 0){
                place_holder = paymentline.user_payment_reference
            } 
        }

        let { confirmed, payload: code } = await this.popup.add(TextInputPopup, {
              title: _t('Payment Reference'),
              startingValue: '',
              placeholder: place_holder ,
          });
        if (confirmed) {
           code = code.trim();
                if (code !== '') {
                    try {
                        // 1. Save Updated to server.
                        // var syncOrderResult = await this.pos.push_state_updates(customer_checklist_dict);
                        let result = await this.pos.check_ref_exist(code)
                        if (result){
                            this.popup.add(ErrorPopup, {
                                title: _t("Duplication"),
                                body: _t("Reference ID Confirmed already or Used."),
                            });
                            return false
                        }
                    } catch (error) {
                        if (error instanceof ConnectionLostError) {
                            const codeExists = this.pos.references.includes(code);
                            if (codeExists){
                                this.popup.add(ErrorPopup, {
                                    title: _t("Duplication"),
                                    body: _t("Reference ID Confirmed already or Used."),
                                });
                                return false
                            }

                        }
                    }
                    this.pos.references.push(code)
                    paymentline.user_payment_reference = code
                    order_list.push({'name':this.pos.get_order().name,
                                     'code': code})
                }
        }
    },
 
});

patch(Payment.prototype, {
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        var user_payment_reference = ''
        if (json.user_payment_reference != undefined){
            user_payment_reference = json.user_payment_reference
        }
        this.user_payment_reference = user_payment_reference;
    },
    export_as_JSON() {
        const result = super.export_as_JSON(...arguments);
        var user_payment_reference = ''
        if (this.user_payment_reference != undefined){
        user_payment_reference = this.user_payment_reference;
        }
        return Object.assign(result, {
            user_payment_reference: user_payment_reference,
        });
        return result
    },
});

