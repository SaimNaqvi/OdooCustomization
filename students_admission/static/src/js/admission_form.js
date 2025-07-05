odoo.define('school_admission.admission_form', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {
        $('#stu_reg_no_search_btn').click(function () {
            var reg_number = $('#stu_reg_no_search').val();
            var branch_id = $('#branch_name').val();
            if (branch_id && reg_number) {
                ajax.jsonRpc('/student/admission/search', 'call', {
                    'reg_number': reg_number,
                    'branch_id': branch_id
                }).then(function (data) {
                    if (data) {
                        $('#stu_reg_no').val(data.stu_reg_no);
                        $('#stu_test_date').val(data.stu_test_date);
                        $('#stu_test_status').val(data.stu_test_status);
                        $('#stu_status').val(data.stu_status);
                        $('#stu_class').val(data.stu_class);
                        $('#stu_section').val(data.stu_section);
                        $('#stu_firstname').val(data.stu_firstname);
                        $('#stu_lastname').val(data.stu_lastname);
                        $('#stu_gender').val(data.stu_gender);
                        $('#stu_religion').val(data.stu_religion);
                        $('#stu_dob').val(data.stu_dob);
                        $('#stu_address').val(data.stu_address);
                        $('#stu_cnic').val(data.stu_cnic);
                        $('#stu_state').val(data.stu_state);
                        $('#stu_city').val(data.stu_city);
                        $('#stu_pre_school_name').val(data.stu_pre_school_name);
                        $('#stu_email').val(data.stu_email);
                        $('#stu_email').val(data.stu_email);
                        $('#admission_date').val(data.admission_date);
                        $('#par1_qtn1').val(data.par1_qtn1);
                        //Parent 1 Information
                        $('#par1_relation_type').val(data.par1_relation_type);
                        $('#par1_salutation').val(data.par1_salutation);
                        $('#par1_firstname').val(data.par1_firstname);
                        $('#par1_lastname').val(data.par1_lastname);
                        $('#par1_gender').val(data.par1_gender);
                        $('#par1_religion').val(data.par1_religion);
                        $('#par1_dob').val(data.par1_dob);
                        $('#par1_cnic').val(data.par1_cnic);
                        $('#par1_phone').val(data.par1_phone);
                        $('#par1_email').val(data.par1_email);
                        $('#par1_edu_level').val(data.par1_edu_level);
                        $('#par1_occupation').val(data.par1_occupation);
                        //Parent 2 Information
                        $('#par2_relation_type').val(data.par2_relation_type);
                        $('#par2_salutation').val(data.par2_salutation);
                        $('#par2_firstname').val(data.par2_firstname);
                        $('#par2_lastname').val(data.par2_lastname);
                        $('#par2_gender').val(data.par2_gender);
                        $('#par2_religion').val(data.par2_religion);
                        $('#par2_dob').val(data.par2_dob);
                        $('#par2_cnic').val(data.par2_cnic);
                        $('#par2_phone').val(data.par2_phone);
                        $('#par2_email').val(data.par2_email);
                        $('#par2_edu_level').val(data.par2_edu_level);
                        $('#par2_occupation').val(data.par2_occupation);
                        // Emergency Contact 1 Information
                        $('#ec1_relation_type').val(data.ec1_relation_type);
                        $('#ec1_firstname').val(data.ec1_firstname);
                        $('#ec1_lastname').val(data.ec1_lastname);
                        $('#ec1_phone').val(data.ec1_phone);
                        // Emergency Contact 2 Information
                        $('#ec2_relation_type').val(data.ec2_relation_type);
                        $('#ec2_firstname').val(data.ec2_firstname);
                        $('#ec2_lastname').val(data.ec2_lastname);
                        $('#ec2_phone').val(data.ec2_phone);
                        // Sibling 1 Information
                        $('#sib1_branch_name').val(data.sib1_branch_name);
                        $('#sib1_roll_no').val(data.sib1_roll_no);
                        $('#sib1_class').val(data.sib1_class);
                        $('#sib1_firstname').val(data.sib1_firstname);
                        $('#sib1_lastname').val(data.sib1_lastname);
                        // Sibling 2 Information
                        $('#sib2_branch_name').val(data.sib2_branch_name);
                        $('#sib2_roll_no').val(data.sib2_roll_no);
                        $('#sib2_class').val(data.sib2_class);
                        $('#sib2_firstname').val(data.sib2_firstname);
                        $('#sib2_lastname').val(data.sib2_lastname);
                        // Sibling 3 Information
                        $('#sib3_branch_name').val(data.sib3_branch_name);
                        $('#sib3_roll_no').val(data.sib3_roll_no);
                        $('#sib3_class').val(data.sib3_class);
                        $('#sib3_firstname').val(data.sib3_firstname);
                        $('#sib3_lastname').val(data.sib3_lastname);


//                        $('#admission_details').show();
//                        $('#phone_number').val(data.phone_number);
//                        $('#relationship_type').val(data.relationship_type);
//                        $('#parent_cnic').val(data.parent_cnic);
                        $('#student_not_found').hide();

                        // Trigger the change event to evaluate the visibility of additional fields
//                        $('#enrollment_status').trigger('change');
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


        $('#stu_status, #test_status').change(function () {
            var enrollment_status = $('#stu_status').val();
            var test_status = $('#test_status').val();
            console.log('Enrollment Status:', enrollment_status);
            console.log('Test Status:', test_status);
            if (enrollment_status === 'Admission' && test_status === 'Pass') {
                console.log('Showing additional fields');
                $('#additional_fields').show();
            } else {
                console.log('Hiding additional fields');
                $('#additional_fields').hide();
            }
        });
    });
});
