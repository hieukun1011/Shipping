# -*- coding: utf-8 -*-

import logging

from .test_quiz_common import TestQuizCommon


class TestQuizCategory(TestQuizCommon):

    def setUp(self):
        super(TestQuizCategory, self).setUp()

    def test_case_1_quiz_category(self):
        categories = self.op_category.search([])

        if not categories:
            raise AssertionError(
                'Error in data, please check for Quiz Categories')
        logging.info('Details of quiz categories')
        logging.info('  Name     :   Code')
        for category in categories:
            logging.info('%s :    %s' % (category.name, category.code))
