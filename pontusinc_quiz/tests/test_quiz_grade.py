# -*- coding: utf-8 -*-

import logging

from .test_quiz_common import TestQuizCommon


class TestQuizGrade(TestQuizCommon):

    def setUp(self):
        super(TestQuizGrade, self).setUp()

    def test_case_2_quiz_grade(self):
        grades = self.op_grade.search([])
        if not grades:
            raise AssertionError(
                'Error in data, please check for Quiz Grades')
        logging.info('Details of quiz grades')
        logging.info('  Name     :   Grades(%)')
        for grade in grades:
            logging.info('%s :    %s' % (grade.name, grade.value))
