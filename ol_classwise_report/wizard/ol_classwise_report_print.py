from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.http import request
import base64, io, datetime
try: import xlwt
except ImportError: xlwt = None

class ClasswiseReport(models.Model):
    _inherit = "invoice.report"

    def print_classwise_report(self):
        # report = self.env['ir.actions.report'].search([('id', '=', 449)])
        # # raise UserError(report)
        # return report.report_action(self)
        return self.env.ref('ol_classwise_report.ol_billing_report_classwise_id').report_action(self)
    
    def print_defaulter_report(self):
        report = self.env['ir.actions.report'].search([('id', '=', 452)])
        return report.report_action(self)

    def print_defaulter_report_excel(self):
        if xlwt==None:
            raise Warning (""" You Don't have xlwt library.\n Please install it by executing this command :  sudo pip3 install xlwt""")

        report_name = "Defaulter Students Report"
        file_name = "Defaulter Students Report.xls"
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Defaulter Students')

        # styles and formatting for cells
        schola_head_style = xlwt.easyxf(f"font:bold on, color white, height 320; align: "
                                        f"vertical center, horiz center; "
                                        f"pattern: pattern solid, fore_color black; "
                                        f"border: top thick, right thick, left thick; ")
        
        schola_addr_style = xlwt.easyxf(f"align: vertical center,horiz center; "
                                        f"border: right thick, left thick; ")

        schola_style = xlwt.easyxf(f"font:bold on, height 260; align: vertical center,horiz center; "
                                   f"border: bottom thick, right thick, left thick; ")

        class_header_style = xlwt.easyxf(f"font:bold on,; align: vertical center,horiz center; "
                                   f"border: top thin, bottom thin, left thin; "
                                   f"pattern: pattern solid, fore_colour lavender;")
        
        section_header_style = xlwt.easyxf(f"font:bold on,; align: vertical center,horiz center; "
                                   f"border: top thin, bottom thin, right thin; "
                                   f"pattern: pattern solid, fore_colour lavender;")

        style_header = xlwt.easyxf(f"font:bold on,; align: vertical center,horiz center; "
                                   f"border: top thin, bottom thin, right thin, left thin;"
                                   f"pattern: pattern solid, fore_colour grey25;")

        style_data = xlwt.easyxf(f"align: vertical center,horiz center; "
                                 f"border: top thin, bottom thin, right thin, left thin;")

        unpaid_fee_style = xlwt.easyxf(f"font:bold on,; align: vertical center,horiz center; "
                                       f"border: top thin, bottom thin, left thin;")

        unpaid_fee_style_value = xlwt.easyxf(f"font:bold on,; align: vertical center,horiz left; "
                                             f"border: top thin, bottom thin, right thin;")

        total_unpaid_fee_style = xlwt.easyxf(f"font:bold on,; align: vertical center,horiz center; "
                                             f"border: top thin, bottom thin, left thin;"
                                             f"pattern: pattern solid, fore_colour yellow;")

        total_unpaid_fee_style_value = xlwt.easyxf(f"font:bold on,; align: vertical center,horiz left; "
                                                   f"border: top thin, bottom thin, right thin;"
                                                   f"pattern: pattern solid, fore_colour yellow;")

        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy'

        # Main headers
        worksheet.write_merge(1, 3, 1, 13, "Schola Nova", style=schola_head_style)
        worksheet.write_merge(4, 4, 1, 13, "Street 8, House#5, F-8/3, Islamabad. 051-2855003", style=schola_addr_style)
        worksheet.write_merge(5, 6, 1, 13, "Admitted Students Defaulter List of Session: 2022-23", style=schola_style)
        
        row = 9

        students = self.env['res.partner'].search([('title','=','Student')]).sorted(key=lambda r: r.grade_no)
        classes = []
        total_amount_school = 0

        for user in students:
            invoices = self.env['account.move'].search([('x_studio_class','=', user.current_grade),('state','=', 'posted'), ('invoice_date_due','<',datetime.datetime.today()),'|',('payment_state','=', 'not_paid'),('payment_state','=', 'partial')])
            if invoices:
                current_class = user.current_grade
                if current_class not in classes and user.current_grade != False and user.current_grade != '':
                    classes.append(current_class)

                    #headers for the table of current class
                    worksheet.write_merge(row, row+1, 1, 2, "Class: Grade "+str(current_class), style=class_header_style)
                    worksheet.write_merge(row, row+1, 3, 13, "Section: S", style=section_header_style)
                    row += 2
                    worksheet.write_merge(row, row+1, 1, 1, "RegNo", style=style_header)
                    worksheet.write_merge(row, row+1, 2, 5, "Name", style=style_header)
                    worksheet.write_merge(row, row+1, 6, 7, "Phone No", style=style_header)
                    worksheet.write_merge(row, row+1, 8, 9, "Fee Month", style=style_header)
                    worksheet.write_merge(row, row+1, 10, 10, "Slip No", style=style_header)
                    worksheet.write_merge(row, row+1, 11, 12, "Due Date", style=style_header)
                    worksheet.write_merge(row, row+1, 13, 13, "Slip Amt", style=style_header)
                    row += 2

                    sections = []
                    total_amount_class = 0
                    for unpaid in invoices:
                        if unpaid.partner_id.phone==False: unpaid.partner_id.phone='' #because some phone numbers were of boolean value False
                        #data inside the table for the current class
                        worksheet.write_merge(row, row+1, 1, 1, unpaid.x_studio_facts_id, style=style_data)
                        worksheet.write_merge(row, row+1, 2, 5, unpaid.partner_id.name, style=style_data)
                        worksheet.write_merge(row, row+1, 6, 7, unpaid.partner_id.phone, style=style_data)
                        worksheet.write_merge(row, row+1, 8, 9, str(unpaid.invoice_date), style=style_data)
                        worksheet.write_merge(row, row+1, 10, 10, unpaid.name, style=style_data)
                        worksheet.write_merge(row, row+1, 11, 12, str(unpaid.invoice_date_due), style=style_data)
                        worksheet.write_merge(row, row+1, 13, 13, unpaid.amount_total, style=style_data)
                        total_amount_class += unpaid.amount_total
                        row += 2

                    #Total unpaid fees for the current class
                    worksheet.write_merge(row, row+1, 9, 11, "Section Total Unpaid Fee:", style=unpaid_fee_style)
                    worksheet.write_merge(row, row+1, 12, 13, total_amount_class, style=unpaid_fee_style_value)
                    total_amount_school += total_amount_class
                    row += 4

        #Total unpaid fee amount of the school
        worksheet.write_merge(row, row+1, 9, 11, "Total Unpaid Fee Amount:",style=total_unpaid_fee_style)            
        worksheet.write_merge(row, row+1, 12, 13, total_amount_school,style=total_unpaid_fee_style_value)     

        fp = io.BytesIO()
        workbook.save(fp)

        export_id = self.env['sale.day.book.report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': file_name})
        res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'sale.day.book.report.excel',
                'type': 'ir.actions.act_window',
                'target':'new'
            }
        return res
