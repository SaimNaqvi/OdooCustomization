from odoo import models, fields,api
from odoo.exceptions import UserError
from datetime import datetime 
import io
import base64
import xlwt


class CustomContactReport(models.Model):
    _name = "custom.contact.report"


    start_date=fields.Date(string="Start date")
    end_date=fields.Date(string="End date:")

    def print_xlsx(self):
        if xlwt:
            report_name = 'Student Report'
            filename = 'Student Report.xls'

            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Student Report')
            style_title = xlwt.easyxf(
            "font:bold on,; align: vertical center,horiz center; border: top thin, bottom thin, right thin, left thin")


            heading_style = xlwt.easyxf('pattern: pattern solid, fore_colour black;'
                              'font: colour white, bold True;')
            
            
            
            for col_index in range(0, 6):
                worksheet.col(col_index).width = 25 * 256
            
            #class N
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','N')])

            heading_fields=[' ','Class: N','Section: S','Session: 2022-23',' ']

            for col, field_name in enumerate(heading_fields):
                worksheet.write(0, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']

            for col, field_name in enumerate(field_names):
                worksheet.write(1, col, field_name, style=style_title)


            row = 2

            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class KG
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','KG')])

            heading_fields=[' ','Class: KG','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class TP
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','TP')])

            heading_fields=[' ','Class: TP','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1
            
            #class I
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','I')])

            heading_fields=[' ','Class: I','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class II
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','II')])

            heading_fields=[' ','Class: II','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class III
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','III')])

            heading_fields=[' ','Class: III','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class IV
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','IV')])

            heading_fields=[' ','Class: IV','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1
            

            #class V
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','V')])

            heading_fields=[' ','Class: V','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class VI
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','VI')])

            heading_fields=[' ','Class: VI','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class VII
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','VII')])

            heading_fields=[' ','Class: VII','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class VIII
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','VIII')])

            heading_fields=[' ','Class: VIII','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class IX
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','IX')])

            heading_fields=[' ','Class: IX','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1

            #class X
            contacts=self.env['res.partner'].search([('is_company', '=', False),('current_enroll_status','=','Enrolled'),('current_grade','=','X')])

            heading_fields=[' ','Class: X','Section: S','Session: 2022-23',' ']
            row+=1
            for col, field_name in enumerate(heading_fields):
                worksheet.write(row, col, field_name, style=heading_style)

            field_names = ['RegNo', 'Name', 'FatherName', 'BirthDate', 'Remarks']
            row+=1
            for col, field_name in enumerate(field_names):
                worksheet.write(row, col, field_name, style=style_title)
            row+=1
            for record in contacts:
                worksheet.write(row, 0, str(record.facts_id))
                worksheet.write(row, 1, record.display_name)
                if record.parent_name:
                    worksheet.write(row, 2, record.parent_name)
                else:
                    for name in record.student_relationship_ids:
                        if name['relationship_type']=='Father':
                            worksheet.write(row, 2, name.parent_id.name)
                            break
                worksheet.write(row, 3, str(record.dob))

                row+=1


            fp = io.BytesIO()
            workbook.save(fp)


            export_id = self.env['sale.day.book.report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
            res = {
                    'view_mode': 'form',
                    'res_id': export_id.id,
                    'res_model': 'sale.day.book.report.excel',
                    'type': 'ir.actions.act_window',
                    'target':'new'
                }
            return res
            
        else:
            raise Warning (""" You Don't have xlwt library.\n Please install it by executing this command :  sudo pip3 install xlwt""")

class sale_day_book_report_excel(models.TransientModel):
    _name = "sale.day.book.report.excel"
    _description = "Sale Day Book Report Excel"
    
    
    excel_file = fields.Binary('Excel Report For Contacts')
    file_name = fields.Char('Excel File', size=64)
