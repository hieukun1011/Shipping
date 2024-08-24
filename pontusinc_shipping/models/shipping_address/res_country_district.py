# -*- coding: utf-8 -*-
from ...util import api_category_vnpost, api_ghn
from odoo import fields, api, models, _
import requests
import re
import json


class CountryDistrict(models.Model):
    _inherit = "res.country.district"

    code_ghn = fields.Char('Code GHN')
    code_ghtk = fields.Char('Code GHTK')
    code_vtpost = fields.Char('Code Viettel Post')

    # def init(self):
    #     url = api_category_vnpost.URL_API_VNPOST + api_category_vnpost.get_all_district
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
    #             district = self.search([('code', '=', rec.get('districtCode'))])
    #             if not district:
    #                 city = self.env['res.country.state'].sudo().search([('code_vnpost', '=', rec.get('provinceCode'))])
    #                 if city:
    #                     vals.append({
    #                         'name': rec.get('districtName'),
    #                         'code': rec.get('districtCode'),
    #                         'state_id': city[0].id
    #                     })
    #         self.sudo().create(vals)

    def sync_district_ghn(self):
        url = api_ghn.URL + api_ghn.get_district
        list_vals = []
        headers = {
            'token': '62771f40-a3a7-11ee-b1d4-92b443b7a897',
            'Content-Type': 'application/json',
        }
        for record in self.env['res.country.state'].sudo().search(
                [('country_id', '=', self.env.ref('base.vn').id), ('code_ghn', '!=', False)]):
            template = {
                "province_id": int(record.code_ghn)
            }
            session = requests.Session()
            response = session.get(url, data=json.dumps(template), headers=headers)
            if response.status_code == 200:
                data = response.json()
                for rec in data.get('data'):
                    modified_name = re.sub(
                        r'\b(Quận |Quận\. |Quan |Quan\. |Q |Q\. |quan |quan\. |Huyện |Huyện\. |H |H. |Huyen |Huyen\. |huyen |huyen\.)\b',
                        '', rec.get('DistrictName'))
                    district = self.search([('state_id.code_ghn', '=', rec.get('ProvinceID'))])
                    if district:
                        district.code_ghn = rec.get('DistrictID')
                    else:
                        list_vals.append({
                            'code_ghn': rec.get('DistrictID'),
                            'name': modified_name,
                            'state_id': record.id
                        })
        if list_vals:
            self.sudo().create(list_vals)
