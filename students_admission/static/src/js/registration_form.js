odoo.define('school_admission.registration_form', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {

        $('#stu_reg_no_search_btn_on_reg_form').click(function () {
            var reg_number = $('#stu_reg_no_search').val();
            var branch_id = $('#branch_name').val();
            if (branch_id && reg_number) {
                ajax.jsonRpc('/student/registration/search', 'call', {
                    'reg_number': reg_number,
                    'branch_id': branch_id
                }).then(function (data) {
                    if (data) {
                        $('#stu_reg_no').val(data.stu_reg_num);
                        $('#reg_stu_firstname').val(data.stu_firstname);
                        $('#reg_stu_lastname').val(data.stu_lastname);
                        $('#reg_stu_class').val(data.reg_stu_class);
                        $('#stu_test_date').val(data.stu_test_date);
                        $('#stu_test_status').val(data.stu_test_status);
                    } else {
                        alert('No student found with this registration number.');
                    }
                });
            }
        });


        $('#par_cnic_search_btn').click(function () {
            var parent_cnic_no = $('#par_cnic_search').val();
            if (parent_cnic_no) {
                ajax.jsonRpc('/student/student/parent', 'call', {
                    'parent_cnic_no': parent_cnic_no,
                }).then(function (data) {
                    if (data) {
                        $('#par_firstname').val(data.par_firstname);
                        $('#par_lastname').val(data.par_lastname);
                        $('#par_gender').val(data.par_gender);
                        $('#par_religion').val(data.par_religion);
                        $('#par_relation_type').val(data.par_relation_type);
                        $('#par_cnic').val(data.par_cnic);
                        $('#par_phone').val(data.par_phone);
                        $('#par_email').val(data.par_email);
                        $('#student_not_found').hide();
                        $('#stu_test_status').trigger('change');
                    } else {
                        $('#admission_details').hide();
                        $('#student_not_found').show();
                    }
                });
            } else {
                alert('Please select a branch and enter a registration number');
            }
        });

    });
});
