"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging
from bs4 import BeautifulSoup
from odoo import http
# from odoo.addons.jwt_provider.JwtRequest import jwt_request
from odoo.http import request
import requests
import json
_logger = logging.getLogger(__name__)


# class WebhookAutoUpdateStateShipping(http.Controller):

# @http.route("/api/v1/update-state-waybill", type="json", auth='public', csrf=False, cors='*', methods=['POST'])
# def api_update_state_waybill(self, **payload):
#     try:
#         payload = request.get_json_data()
#         for data in payload:
#             if data.get('originalId'):
#                 shipping = self.env['shipping.waybill'].sudo().search(
#                     [('code_shipping', '=', data.get('originalId'))])
#                 if shipping:
#                     vals = {
#                         'state_id': self.env['shipping.state'].sudo().search([('code', '=', data.get('status')),
#                                                                               ('platform_id', '=', self.env.ref(
#                                                                                   'pontusinc_shipping.shipping_platform_vnpost').id)]),
#
#                     }
#     except Exception as ie:
#         result = response.response_500('Server error', ie)
#         return jwt_request.response_500(result)
#     return jwt_request.response(payload)
class PrintGHNController(http.Controller):

    def get_token(self, code_shipping):
        url = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/a5/gen-token'
        headers = {
            'token': request.env.user.token_ghn,
            'Content-Type': 'application/json',
        }
        template = {
            "order_codes": [code_shipping]
        }
        session = requests.Session()
        response = session.post(url, data=json.dumps(template), headers=headers)
        data = response.json()
        if response.status_code == 200:
            return data.get('data').get('token')
        return False

    @http.route('/web/print_html_view', type='http', auth='user')
    def print_html_view(self, **kwargs):
        if kwargs.get('code_shipping'):
            token = self.get_token(kwargs.get('code_shipping', ''))
            url = 'https://dev-online-gateway.ghn.vn/a5/public-api/printA5?token=%s' %token
            session = requests.Session()
            response = session.get(url)
            # Trả về trang HTML với script để tự động in
            return request.make_response(f"""
                        <html>
                        <head>
                            <meta charset="UTF-8" />
                            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                            <title>Print Page</title>
                        </head>
                        <body onload="window.print();">
                            {response.text}
                        </body>
                        </html>
                    """)
