odoo.define('fee_manager.StudentBillCharField', function (require) {
    "use strict";

    const FieldChar = require('web.basic_fields').FieldChar;
    const fieldRegistry = require('web.field_registry');
    const rpc = require('web.rpc');

    const StudentBillCharField = FieldChar.extend({
        events: _.extend({}, FieldChar.prototype.events, {
            'keydown': '_onKeydown',
        }),

        _onKeydown: function (ev) {
            if (ev.key === 'Enter') {
                const bill_number = this.value;

                rpc.query({
                    model: 'account.payment',
                    method: 'get_bill_details',
                    args: [bill_number],
                }).then((result) => {
                    if (result && result.partner_id) {
                        this._setValue('');
                        this.trigger_up('field_changed', {
                            dataPointID: this.recordData.id,
                            changes: {
                                partner_id: result.partner_id,
                                amount: result.amount,
                                ref: result.reference,
                                student_bill: bill_number, // Keep bill number
                            },
                        });
                    } else {
                        this.do_warn('Warning', 'No Bill found for this number.');
                    }
                });
            }
        },
    });

    fieldRegistry.add('student_bill_char', StudentBillCharField);

    return StudentBillCharField;
});
