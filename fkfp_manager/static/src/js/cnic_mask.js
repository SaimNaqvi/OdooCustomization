/** @odoo-module **/

import { Component, onRendered } from "@odoo/owl";
import { registry } from "@web/core/registry";

class CNICMask extends Component {
    static template = "fkfp_manager.CNICMaskTemplate";  // your dummy template
    static props = {};  // empty props definition (required by Owl)

    setup() {
        onRendered(() => {
            const inputs = document.querySelectorAll(".o_form_view .cnic_mask input");
            if (window.jQuery && window.jQuery.fn.inputmask) {
                inputs.forEach(el => {
                    window.jQuery(el).inputmask("99999-9999999-9");
                });
                console.log("✅ CNIC mask applied");
            } else {
                console.warn("❌ jQuery or Inputmask not available.");
            }
        });
    }
}

// Register the component
registry.category("main_components").add("cnic_mask_component", {
    Component: CNICMask,
});
