# -*- coding: utf-8 -*-

import logging

from .test_quiz_common import TestQuizCommon


class TestQueBank(TestQuizCommon):

    def setUp(self):
        super(TestQueBank, self).setUp()

    def test_case_4_que_bank(self):
        banks = self.op_que_bank.search([])
        if not banks:
            raise AssertionError(
                'Error in data, please check for Question Bank')
        logging.info('Details of Question Bank')
        logging.info('Name  :       Type        :   #Questions')
        for bank in banks:
            lines = len(
                self.op_que_bank_line.search([('bank_id', '=', bank.id)]))
            if not lines:
                raise AssertionError(
                    'Error in data, please check '
                    'for number of questions for %s' % bank.name)
            logging.info('%s    : %s    : %d' % (
                bank.name, bank.bank_type.name, lines))
