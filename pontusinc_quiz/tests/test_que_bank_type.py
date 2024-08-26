# -*- coding: utf-8 -*-

import logging

from .test_quiz_common import TestQuizCommon


class TestQueBankType(TestQuizCommon):

    def setUp(self):
        super(TestQueBankType, self).setUp()

    def test_case_3_que_bank_type(self):
        types = self.op_que_bank_type.search([])
        if not types:
            raise AssertionError(
                'Error in data, please check for Question Bank types')
        logging.info('Details of Question Bank Types')
        logging.info('Name  ::')
        for type in types:
            logging.info('%s' % type.name)
