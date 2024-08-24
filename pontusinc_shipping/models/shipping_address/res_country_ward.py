# -*- coding: utf-8 -*-
from ...util import api_category_vnpost, api_ghn
from odoo import fields, api, models, _
import requests
import re
import json

class CountryWard(models.Model):
    _inherit = "res.country.ward"

    code_ghn = fields.Char('Code GHN')
    code_ghtk = fields.Char('Code GHTK')
    code_vtpost = fields.Char('Code Viettel Post')

    # def init(self):
    #     url = api_category_vnpost.URL_API_VNPOST + api_category_vnpost.get_all_commune
    #     headers = {
    #         'token': 'CCBM0a0WqkVPAvIDw3ph+03x9WPP4VgfwesmEa53gNqyvmcnbDoI/aqWaUYyo+h5ej6iUA5N9ZEjHfn9RsXvbnWdmz/XLInbxSO8aDeU8iMmzJDnrahqLIvUF9BQaSb9'
    #     }
    #     session = requests.Session()
    #     response = session.get(url, headers=headers)
    #
    #     if response.status_code == 200:
    #         data = response.json()
    #         vals = []
    #         for rec in data:
    #             ward = self.search([('code', '=', rec.get('communeCode'))])
    #             if not ward:
    #                 district = self.env['res.country.district'].sudo().search([('code', '=', rec.get('districtCode'))])
    #                 if district:
    #                     vals.append({
    #                         'name': rec.get('communeName'),
    #                         'code': rec.get('communeCode'),
    #                         'district_id': district[0].id
    #                     })
    #         self.sudo().create(vals)

    def sync_ward_ghn(self):
        url = api_ghn.URL + api_ghn.get_ward
        list_vals = []
        headers = {
            'token': '62771f40-a3a7-11ee-b1d4-92b443b7a897',
            'Content-Type': 'application/json',
        }
        for record in self.env['res.country.district'].sudo().search([('code_ghn', '!=', False)]):
            template = {
                "district_id": int(record.code_ghn)
            }
            session = requests.Session()
            response = session.get(url, data=json.dumps(template), headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    for rec in data.get('data'):
                        modified_name = re.sub(
                            r'\b(Phường |Phường\. |Phuong |Phuong\. |P |P\. |xa |xa\. |Xã |Xã\. |X |X. |Xa |Xa\. |Thị trấn)\b',
                            '', rec.get('WardName'))
                        district = self.search([('district_id.code_ghn', '=', rec.get('DistrictID'))])
                        if district:
                            district.code_ghn = rec.get('WardCode')
                        else:
                            list_vals.append({
                                'code_ghn': rec.get('WardCode'),
                                'name': modified_name,
                                'district_id': record.id
                            })
        if list_vals:
            self.sudo().create(list_vals)