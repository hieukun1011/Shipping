# -*- coding: utf-8 -*-
import requests
from odoo import fields, api, models, _
from ...util import api_category_vnpost, api_ghn
import re

class CountryCity(models.Model):
    _inherit = "res.country.state"

    area_id = fields.Many2one('area.shipping', string='Area')
    code_ghn = fields.Char('Code GHN')
    code_ghtk = fields.Char('Code GHTK')
    code_vtpost = fields.Char('Code Viettel Post')

    # def init(self):
    #     url = api_category_vnpost.URL_API_VNPOST + api_category_vnpost.get_all_city
    #     headers = {
    #         'token': 'CCBM0a0WqkVPAvIDw3ph+03x9WPP4VgfwesmEa53gNqyvmcnbDoI/aqWaUYyo+h5ej6iUA5N9ZEjHfn9RsXvbnWdmz/XLInbxSO8aDeU8iMmzJDnrahqLIvUF9BQaSb9'
    #     }
    #     session = requests.Session()
    #     response = session.get(url, headers=headers)
    #
    #     if response.status_code == 200:
    #         data = response.json()
    #         for rec in data:
    #             modified_name = re.sub(r'\b(Tỉnh |TP\. )\b', '', rec.get('provinceName'))
    #             city = self.search([('name', 'ilike', modified_name)])
    #             if city:
    #                 city.code_vnpost = rec.get('provinceCode')

    def sync_city_ghn(self):
        url = api_ghn.URL + api_ghn.get_province
        headers = {
            'token': '62771f40-a3a7-11ee-b1d4-92b443b7a897'
        }
        session = requests.Session()
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            list_vals = []
            data = response.json()
            for rec in data.get('data'):
                modified_name = re.sub(r'\b(Tỉnh |TP\. )\b', '', rec.get('ProvinceName'))
                city = self.search([('name', '=', modified_name)])
                if city:
                    city.code_ghn = rec.get('ProvinceID')
                else:
                    list_vals.append({
                        'code_ghn': rec.get('ProvinceID'),
                        'name': modified_name,
                        'country_id': self.env.ref('base.vn').id
                    })
            if list_vals:
                self.sudo().create(list_vals)