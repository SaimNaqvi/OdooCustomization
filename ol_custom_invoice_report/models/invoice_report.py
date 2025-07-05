from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import base64
import io
import json

try:
    import xlwt
except ImportError:
    xlwt = None

# ---------------------------M Arsalan

class ProductTag(models.Model):
    _name = "product.tag"
    _description = "Product Tag"
   
    name = fields.Char(string='Name' , required=True , tracking=True)

class ResConfigSettings(models.TransientModel):
    _inherit ='res.config.settings'

    tag_ids = fields.Many2many("product.tag" , string="Product Tags")
    # cancel_days = fields. Integer (string='Cancel Days', config_parameter='om_hospital.cancel_day')  ,

# ---------------------------M Arsalan

class sale_day_book_report_excel(models.TransientModel):
    _name = "invoice.report.excel"
    _description = "Invoice Report Excel"

    excel_file = fields.Binary('Excel Report For Invoices ')
    file_name = fields.Char('Excel File', size=64)


class CustomInvoiceReport(models.Model):
    _name = 'invoice.report'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")

    def generate_report(self):
        if xlwt:
            if not self.date_from or not self.date_to:
                raise UserError("Please enter the Date Range")
            report_name = 'Daily Paid Fee Report'
            filename = 'Daily Paid Fee Reports.xls'
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('report')

            style_title = xlwt.easyxf(
                "font:bold on,; align: vertical center,horiz center; border: top thin, bottom thin, right thin, left thin")

            data_dict = {"RegNo": [], "StudentName": [], "StudentClass": [], "StudentFatherName": [],
                         "FatherNIDCardNo": [],
                         "StudentMotherName": [], "MotherNIDCardNo": [], "FeeMonth": [], "Techerspackage": [],"Tuition Fee": [],
                         "Fee Concession": [], "E-Portal Charges": [], "Exam & Photocopy Charges": [],
                         "Welcome/Farewell": [], "Photocopy & Jolly Learning Resource": [],
                         "Instructional Material (V-VII)": [],
                         "NetTutionFee": [], "LateFee": [],"LateFeeFine": [],
                         "TurkishBookCharges": [], "Discount": [],
                           "TotalFee": [], "AmountPaid": [],"AmntDue": [], "PaidDate": []}

            invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'),
                                                        ('state', '=', 'posted'),
                                                        # ('payment_state', 'in', ['paid', 'in_payment'])
                                                        ])

            class_order = { 'N': 1,  
                           'PN':2,
                           'DC':3,
                           'KG': 4, 
                           'TP': 5, 
                           'I': 6, 
                           'II': 7, 
                           'III': 8, 
                           'IV': 9, 
                           'V': 10, 
                           'VI': 11, 
                           'VII': 12,
                           'VIII': 13, 
                           'IX': 14, 
                           'X': 15,
                           }

            for rec in invoices:
                payments = self.env['account.payment'].search([('ref', '=', rec.name),
                                                        ('partner_type', '=', 'customer'), 
                                                        ('is_internal_transfer', '=', False)])

                if not payments:
                    continue
                else:      
                    flag=False      
                    amount_paid=0    
                    prev_amount=0
                    for pay in payments:
                        if pay.date<self.date_from :
                            prev_amount+=float(pay.amount)
                            
                        if pay.date>= self.date_from and pay.date <= self.date_to:
                            amount_paid+= float(pay.amount)
                            flag=True
                            paid_date = str(pay.date.strftime('%d/%m/%Y'))
                            
                    amount_due =rec.amount_total-amount_paid-prev_amount
                if flag==False:
                    continue
                    
                registration_no = rec.x_studio_facts_id
                student_name = rec.partner_id.name
                student_class = ''
                if rec.partner_id.current_grade:
                    student_class = rec.partner_id.current_grade
                names = rec.partner_id.student_relationship_ids
                father_name = ''
                mother_name = ''
                father_cnic = ''
                mother_cnic = ''

                for name in names:
                    if name.type == 'Father':
                        father_name = name.partner_id.name
                        if name.partner_id.cnic:
                            father_cnic = name.partner_id.cnic
                    elif name.type == 'Mother':
                        mother_name = name.partner_id.name
                        if name.partner_id.cnic:
                            mother_cnic = name.partner_id.cnic
                    else:
                        father_name = name.partner_id.name
                        if name.partner_id.cnic:
                            father_cnic = name.partner_id.cnic

                # fee_month = datetime.strptime(str(rec.ol_payment_date), '%Y-%m-%d').strftime('%B-%Y')
                # Assuming rec.invoice_date is a datetime object
                fee_month = datetime.strftime(rec.invoice_date, '%B-%Y')

                # Check if the journal name is Quarterly
                if rec.journal_id.name.lower() == 'quarterly':
                    # Determine the start month of the quarter
                    quarter_start_month = (rec.invoice_date.month - 1) // 3 * 3 + 1

                    # Generate the months of the quarter
                    quarter_months = [
                        datetime.strftime(datetime(rec.invoice_date.year, month, 1), '%B-%Y')
                        for month in range(quarter_start_month, quarter_start_month + 3)
                    ]

                    # Update fee_month to contain the months of the quarter
                    fee_month = ','.join(quarter_months)


                teacher_package = "-"
                tuition_fees = 0
                fee_concession = 0
                net_tution_fees = 0
                e_portal_charges = 0
                exam_and_photocopy_charges = 0
                welcome_farewell = 0
                photocopy_and_jolly_learning_resource = 0
                instruction_material = 0
                late_fee = 0
                late_fee_fine = 0
                turkish_book_charges = 0
                discount = 0

                for lines in rec.invoice_line_ids:
                    if lines.product_id.name == "Teacher's Package":
                        teacher_package = lines.price_unit
                    if lines.product_id.name == 'Tuition Fee':
                        tuition_fees = lines.price_unit
                    if lines.product_id.name == 'Fee Concession':
                        fee_concession = lines.price_unit
                    if lines.product_id.name == 'E-Portal Charges':
                        e_portal_charges = lines.price_unit
                    if lines.product_id.name == 'Exam & Photocopy Charges':
                        exam_and_photocopy_charges = lines.price_unit
                    if lines.product_id.name == 'Welcome/Farewell':
                        welcome_farewell = lines.price_unit
                    if lines.product_id.name == 'Photocopy & Jolly Learning Resource':
                        photocopy_and_jolly_learning_resource = lines.price_unit
                    if lines.product_id.id == 73:  # Instructional Material (V-VII)
                        instruction_material = lines.price_unit
                    if lines.product_id.name == 'Late Fee Fine':
                        late_fee_fine = lines.price_unit
                    if lines.product_id.name == 'Late Fee':
                        late_fee = lines.price_unit
                    if lines.product_id.name == "10% Discount":
                        discount = lines.price_unit
                    if lines.product_id.name.lower() == 'turkish book charges':
                        turkish_book_charges = lines.price_unit
                        


                total_fee = rec.amount_total
                net_tution_fees = tuition_fees - fee_concession

                data_dict["RegNo"].append(registration_no)
                data_dict["StudentName"].append(student_name)
                data_dict["StudentClass"].append(student_class)
                data_dict["StudentFatherName"].append(father_name)
                data_dict["FatherNIDCardNo"].append(father_cnic)
                data_dict["StudentMotherName"].append(mother_name)
                data_dict["MotherNIDCardNo"].append(mother_cnic)
                data_dict["FeeMonth"].append(fee_month)
                data_dict["Techerspackage"].append(teacher_package)
                data_dict["Tuition Fee"].append(tuition_fees)
                data_dict["Fee Concession"].append(fee_concession)
                data_dict["E-Portal Charges"].append(e_portal_charges)
                data_dict["Exam & Photocopy Charges"].append(exam_and_photocopy_charges)
                data_dict["Welcome/Farewell"].append(welcome_farewell)
                data_dict["Photocopy & Jolly Learning Resource"].append(photocopy_and_jolly_learning_resource)
                data_dict["Instructional Material (V-VII)"].append(instruction_material)
                data_dict["TurkishBookCharges"].append(turkish_book_charges)
                data_dict["Discount"].append(discount)
                data_dict["TotalFee"].append(total_fee)
                data_dict["LateFee"].append(late_fee)
                data_dict["LateFeeFine"].append(late_fee_fine)
                data_dict["NetTutionFee"].append(net_tution_fees)
                data_dict["AmountPaid"].append(amount_paid)
                data_dict["AmntDue"].append(amount_due)
                data_dict["PaidDate"].append(paid_date)

             # Create a list of tuples with class and index for sorting
            class_and_index = [(class_order[class_value], index) for index, class_value in enumerate(data_dict["StudentClass"])]

            # Sort the indices based on class_order
            sorted_indices = [index for _, index in sorted(class_and_index)]

            # Reorder data_dict based on sorted indices
            for key in data_dict:
                data_dict[key] = [data_dict[key][index] for index in sorted_indices]

            data_dict.pop("NetTutionFee")

            #eliminate zero values column x x   
            zeroKeys=[]
            for key,val in data_dict.items():
                allZero=True
                for item in val:
                    if item!=0:
                        allZero=False
                if allZero==True:
                    zeroKeys.append(key)
            
            for item in zeroKeys:
                if item == "AmntDue":
                    pass
                else:
                    data_dict.pop(item)

            # ...

            # Writing the headers to the worksheet
            col = 0
            for key in data_dict.keys():
                row = 0
                worksheet.write(row, col, key, style=style_title)
                row += 1
                for item in data_dict[key]:
                    worksheet.write(row, col, item)
                    row += 1
                col += 1

            fp = io.BytesIO()
            workbook.save(fp)

            export_id = self.env['invoice.report.excel'].create(
                {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'invoice.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
            return res

        else:
            raise UserError(
                """ You Don't have xlwt library.\n Please install it by executing this command :  sudo pip3 install xlwt""")
