from odoo import models


class ReportCVPDF(models.AbstractModel):
    _name = 'report.fkfp_manager.report_print_pdf'
    _description = 'CV Report'
    _inherit = 'report.report_xlsx.abstract'

    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'fkfp.manager',
            'docs': docs,
        }
