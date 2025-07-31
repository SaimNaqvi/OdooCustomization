/** @odoo-module */
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { useState, Component, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// Patch the Order model to include loyalty points
patch(Order.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);

        // Add customer data
        const partner = this.get_partner();
        if (partner) {
            result.partner = {
                name: partner.name || "Guest",
                total_loyalty_points: partner.total_loyalty_points || 0,
            };
        }
        // Fetch loyalty points for the current order
        const loyaltyPoints = this.getLoyaltyPoints();
        if (loyaltyPoints) {
            const loyaltyStat = loyaltyPoints[0]?.points || {};
            result.loyalty_points_won = loyaltyStat.won || 0; // Points earned
            result.loyalty_points_spent = loyaltyStat.spent || 0; // Points spent
            result.loyalty_points_total = loyaltyStat.total || 0; // Total points
        }

        return result;

        // Calculate and add loyalty points dynamically
        const loyaltyProgram = this.pos.loyalty_program; // Get loyalty program from POS
        if (loyaltyProgram) {
            const earnedPoints = this.get_total_with_tax() * loyaltyProgram.points_per_currency;
            result.loyalty_points = Math.floor(earnedPoints);
        } else {
            result.loyalty_points = 0;
        }

        return result;
    },
});

patch(OrderReceipt.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            template: true,
        });
        this.pos = useState(useService("pos"));
    },
    get templateProps() {
        const pos = this.env.services.pos;
        const order = this.pos.get_order();
        const receipt = order ? order.export_for_printing() : {};
        const operationType = pos.config.picking_type_id[1] || "Default Location";
        receipt.operation_type = operationType;

        if (receipt.name) {
            const parts = receipt.name.split("-");
            receipt.numeric_name = parts.slice(1).join("-");
        }

        return {
            data: this.props.data || { total_without_tax: 0, tax_details: [] },
            order: this.pos.orders,
            receipt,
            orderlines: order ? order.get_orderlines() : [],
            paymentlines: order ? order.get_paymentlines() : [],
        };
    },
    get templateComponent() {
        const mainRef = this;
        return class extends Component {
            setup() {}
            static template = xml`${mainRef.pos.config.design_receipt}`;
        };
    },
    get isTrue() {
        return this.env.services.pos.config.is_custom_receipt === false;
    },
});
