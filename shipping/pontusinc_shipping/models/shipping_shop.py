# -*- coding: utf-8 -*-
import json

import requests

from odoo import fields, models
from ..util import api_ghn


class ShippingShop(models.Model):
    _name = 'shipping.shop'

    name = fields.Char('Name')
    code = fields.Char('Code')
    phone = fields.Char('Phone')
    address = fields.Char('Address')
    city_id = fields.Many2one('res.country.state', string='City')
    district_id = fields.Many2one('res.country.district', string='District')
    ward_id = fields.Many2one('res.country.ward', string='Ward')

    def init(self):
        url = api_ghn.URL + api_ghn.get_shop
        headers = {
            'token': '62771f40-a3a7-11ee-b1d4-92b443b7a897',
            'Content-Type': 'application/json',
        }
        template = {
            "offset": 0,
            "limit": 50,
            "client_phone": ""
        }
        session = requests.Session()
        response = session.post(url, data=json.dumps(template), headers=headers)

        if response.status_code == 200:
            data = response.json()
            vals = []
            for rec in data.get('data').get('shops'):
                shop = self.search([('code', '=', rec.get('_id'))])
                if not shop:
                    vals.append({
                        'name': rec.get('name'),
                        'code': rec.get('_id'),
                        'phone': rec.get('phone'),
                        'address': rec.get('address'),
                    })
            self.sudo().create(vals)

    def create_shop_ghn(self):
        url = api_ghn.URL + api_ghn.create_shop
        headers = {
            'token': '62771f40-a3a7-11ee-b1d4-92b443b7a897',
            'Content-Type': 'application/json',
        }
        template = {
            "district_id": self.district_id.code_ghn,
            "ward_code": self.ward_id.code_ghn,
            "name": self.name,
            "phone": self.phone,
            "address": self.address
        }
        session = requests.Session()
        response = session.get(url, data=json.dumps(template), headers=headers)

        if response.status_code == 200:
            data = response.json()
            for rec in data.get('data'):
                self.code = rec.get('shop_id')
