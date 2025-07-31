from odoo import http, fields
from odoo.http import request, Response
from datetime import datetime
import json
from odoo.addons.web.controllers.main import Session


class CustomSession(Session):
    def authenticate(self, db, login, password, base_location=None):
        response = super(CustomSession, self).authenticate(db, login, password, base_location)
        if response.get('uid'):  # Successful login
            user = request.env['res.users'].sudo().browse(response['uid'])
            user.sudo().write({'api_login_time': datetime.now()})
        return response


class SchoolBillingAPI(http.Controller):
    def _get_api_key(self):
        # Retrieve API key from system parameters in Odoo
        return request.env['ir.config_parameter'].sudo().get_param('bank_api_secret')

    def _validate_api_key(self, key):
        # Compare provided API key with stored API key
        return key == self._get_api_key()

    @http.route('/api/invoices/', type='http', auth="none", methods=['GET'], csrf=False, cors='*')
    def get_student_invoices(self, **kwargs):
        api_key = request.httprequest.headers.get('X-API-KEY')
        if not self._validate_api_key(api_key):
            return Response("Unauthorized", status=401)

        # Retrieve only unpaid and posted invoices for the specified student
        invoices = request.env['account.move'].sudo().search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ])

        # Prepare response data, ensuring date serialization
        data = []
        for invoice in invoices:
            data.append({
                'invoice_id': invoice.id,
                'amount_total': invoice.amount_total,
                'amount_residual': invoice.amount_residual,
                'state': invoice.state,
                # Convert due date to a string
                'due_date': invoice.invoice_date_due.strftime('%Y-%m-%d') if invoice.invoice_date_due else None,
            })
        return Response(json.dumps(data), content_type='application/json')
        # New endpoint to retrieve a single invoice by bill_id

    @http.route('/api/invoice/<int:bill_id>', type='http', auth="none", methods=['GET'], csrf=False, cors='*')
    def get_single_invoice(self, bill_id, **kwargs):
        # Fetch the current user
        user = request.env.user

        # Get session timeout parameter
        session_timeout = int(request.env['ir.config_parameter'].sudo().get_param('api_session_timeout', 3600))

        # Calculate session time left
        if user.api_login_time:
            current_time = datetime.now()
            elapsed_time = (current_time - user.api_login_time).total_seconds()
            time_left = max(0, session_timeout - elapsed_time)

            if time_left <= 0:
                # If session expired
                return Response(json.dumps({
                    'error': 'Session expired. Please log in again.',
                    'session_time_left': 0
                }), content_type='application/json', status=401)
        else:
            return Response(json.dumps({
                'error': 'No login time recorded for the user.',
            }), content_type='application/json', status=401)

        invoice = request.env['account.move'].sudo().search([('name', '=', bill_id)])
        # Check if invoice exists and is valid
        if not invoice.exists() or invoice.move_type != 'out_invoice' or invoice.state != 'posted':
            return Response("Invoice not found or not valid for retrieval", status=404)
        current_date = fields.Date.today()
        amount = 0.0
        if invoice.invoice_date_due < current_date < invoice.due_date_II:
            late_fee_product = request.env['product.product'].sudo().search([('name', '=', 'Late Fee')])
            amount = invoice.amount_total + late_fee_product.list_price
        elif current_date >= invoice.due_date_II:
            second_late_fee_amount = int((300 + invoice.amount_residual) * 0.1)
            amount = invoice.amount_total + second_late_fee_amount
        else:
            amount = invoice.amount_total
        # Prepare response data for a single invoice
        payment_date = None
        if invoice.ol_payment_date_compute is not '':
            payment_date = invoice.ol_payment_date_compute
        payment_status = ''
        if invoice.payment_state == 'in_payment' or invoice.payment_state == 'paid':
            payment_status = 'paid'
        else:
            payment_status = 'not_paid'

        data = {
            'bill_id': invoice.name,
            'payment_status': payment_status,
            'billing_month': invoice.billingMonth,
            'due_date': invoice.invoice_date_due.strftime('%d/%m/%Y'),
            'payment_before_due_date': invoice.amount_total,
            'payment_after_due_date': int(amount),
            'student_name': invoice.partner_id.name,
            'payment_date': payment_date.strftime('%d/%m/%Y') if payment_date else None,
            'session_time_left': time_left
        }
        return Response(json.dumps(data), content_type='application/json')

    @http.route('/api/pay_invoice', type='http', auth="none", methods=['POST'], csrf=False, cors='*')
    def pay_invoice(self, **kwargs):
        # Extract invoice name and payment amount from JSON payload
        invoice_name = "236627"
        payment_amount = "21600"
        payment_date = "13/12/2024"

        # Validation: Missing required parameters
        if not invoice_name:
            return Response(
                json.dumps({'response-code': '001',
                            'status': 'error',
                            'message': 'Invalid or missing bill number',
                            'payment_status': 'Null',
                            'payment_date': 'Null',
                            }),
                content_type='application/json', status=400
            )
        if not payment_amount:
            return Response(
                json.dumps({'response-code': '002',
                            'status': 'error',
                            'message': 'Missing payment amount',
                            'payment_status': 'Null',
                            'payment_date': 'Null',
                            }),
                content_type='application/json', status=400
            )
        if not payment_date:
            return Response(
                json.dumps({'response-code': '003',
                            'status': 'error',
                            'message': 'Invalid or missing payment date. Expected format: DD/MM/YYYY',
                            'payment_status': 'Null',
                            'payment_date': payment_date if payment_date else 'Null',
                            }),
                content_type='application/json', status=400
            )

        if not invoice_name or not payment_amount or not payment_date:
            return Response("Missing invoice_name or payment_amount or ", status=400)

        # Look up the invoice by its unique name
        invoice = request.env['account.move'].sudo().search([('name', '=', invoice_name), ('state', '=', 'posted')],
                                                            limit=1)

        # Check if invoice exists and is unpaid
        if not invoice:
            return Response(json.dumps({'response-code': '004',
                                        'status': 'warning',
                                        'message': 'Invalid entered Bill number or Bill is missing',
                                        'payment_status': 'Null',
                                        'payment_date': 'Null',
                                        }),
                            content_type='application/json', status=404)
        if invoice.payment_state == 'paid' or invoice.payment_state == 'in_payment':
            payment_status = invoice.payment_state
            if invoice.payment_state == 'in_payment' or invoice.payment_state == 'paid':
                payment_status = 'paid'
            else:
                payment_status = 'not_paid'
            return Response(
                json.dumps({'response-code': '005',
                            'status': 'warning',
                            'message': 'Invoice is already paid',
                            'payment_status': payment_status if payment_status else 'Null',
                            'payment_date': payment_date if payment_date else 'Null',
                            }),
                content_type='application/json', status=400
            )
        # Validation: Payment amount matches the invoice amount
        if float(payment_amount) != invoice.amount_total:
            payment_status = invoice.payment_state
            return Response(
                json.dumps({'response-code': '006',
                            'status': 'warning',
                            'message': 'Payment amount mismatch. Entered amount does not match bill amount',
                            'payment_status': payment_status if payment_status else 'Null',
                            'payment_date': payment_date if payment_date else 'Null',
                            }), content_type='application/json', status=400
            )

        # If payment_date is provided, convert it to the correct format ('%Y-%m-%d')
        if payment_date:
            payment_status = invoice.payment_state
            try:
                payment_date = datetime.strptime(payment_date, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                return Response(json.dumps({
                    'response-code': '007',
                    'status': 'warning',
                    'message': 'Invalid payment_date format, use DD/MM/YYYY',
                    'payment_status': payment_status if payment_status else 'Null',
                    'payment_date': payment_date if payment_date else 'Null',
                }), content_type='application/json', status=400)
        # Check if payment date is provided, if not, set it to today's date
        if not payment_date:
            payment_date = fields.Date.today()

        payment_status = ''
        if invoice.payment_state == 'in_payment' or invoice.payment_state == 'paid':
            payment_status = 'paid'
        else:
            payment_status = 'not_paid'

        if invoice.payment_state == 'paid' or invoice.payment_state == 'in_payment':
            response_data = {
                'response-code': '000',
                'status': 'success',
                'message': 'Invoice already marked as paid',
                'payment_status': payment_status,
                'payment_date': invoice.ol_payment_date_compute.strftime(
                    '%d-%b-%y')

            }
            return Response(json.dumps(response_data), content_type='application/json', status=200)

        # Create a payment record
        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': invoice.partner_id.id,
            'amount': payment_amount,
            'currency_id': invoice.currency_id.id,
            'date': payment_date,
            'journal_id': request.env['account.journal'].sudo().search([('type', '=', 'bank')], limit=1).id,
            'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
            'invoice_id': f"{invoice.ref} ({invoice.name})" if invoice.ref else invoice.name
        }
        payment = request.env['account.payment'].sudo().create(payment_vals)

        # Reconcile payment with the invoice
        payment.action_post()
        invoice_line = invoice.line_ids.filtered(lambda line: line.account_id.reconcile and not line.reconciled)
        payment_line = payment.move_id.line_ids.filtered(
            lambda line: line.account_id == invoice_line.account_id and not line.reconciled)

        # Reconcile invoice and payment lines if both are found
        if invoice_line and payment_line:
            (invoice_line + payment_line).reconcile()
        else:
            return Response("No eligible lines for reconciliation or account does not allow reconciliation", status=400)
        # Reload the invoice to get the updated payment status
        invoice.invalidate_cache()
        payment_status = ''
        if invoice.payment_state == 'in_payment' or invoice.payment_state == 'paid':
            payment_status = 'paid'
        else:
            payment_status = 'not_paid'
        response_data = {
            'response-code': '000',
            'status': 'success',
            'message': 'Invoice marked as paid',
            'payment_status': payment_status,
            'payment_date': invoice.ol_payment_date_compute.strftime(
                '%d-%b-%y')

        }
        return Response(json.dumps(response_data), content_type='application/json', status=200)
