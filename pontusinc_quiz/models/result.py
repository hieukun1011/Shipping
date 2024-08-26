# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api, exceptions, _
import logging

from bs4 import BeautifulSoup

from odoo import models, fields, api, exceptions, _
from datetime import datetime

_logger = logging.getLogger(__name__)


class OpQuizResult(models.Model):
    _name = "op.quiz.result"
    _description = "Quiz Results"

    def get_progress_data(self):
        self.ensure_one()
        total = self.total_question
        attempt_ans = 0
        for line in self.line_ids:
            if line.given_answer:
                attempt_ans += 1
        return (attempt_ans * 100) / total

    def get_quiz_grid_data(self, current_line):
        self.ensure_one()
        quiz = self.quiz_id
        data = []
        que_no = 1
        temp = True
        for line in self.line_ids:
            is_ans_given = 0
            is_readonly = 0
            current_id = 0
            if line.id == current_line.id:
                current_id = 1
                temp = False
            if line.given_answer:
                is_ans_given = 1
            if not quiz.prev_allow:
                is_readonly = 1
            if quiz.que_required:
                if not temp and is_ans_given == 0:
                    is_readonly = 1
            data.append({
                'is_ans_given': is_ans_given,
                'is_readonly': is_readonly,
                'line': line,
                'quiz': self,
                'que_no': que_no,
                'current_id': current_id
            })
            que_no += 1
        return data

    def get_answer_data(self):
        self.ensure_one()
        wrong_answers = []
        not_attempt_answer = []
        right_answers = []
        for line in self.line_ids:
            if not line.given_answer:
                not_attempt_answer.append(
                    {'question': line.name, 'answer': line.answer or ''})
            elif line.answer == line.given_answer:
                right_answers.append(
                    {'question': line.name, 'answer': line.answer})
            else:
                wrong_answers.append({
                    'question': line.name,
                    'given_answer': line.given_answer,
                    'answer': line.answer or '',
                })
        quiz = self.quiz_id
        display_wrong_ans = 0
        if quiz.wrong_ans and wrong_answers:
            display_wrong_ans = 1
        display_true_ans = 0
        if quiz.right_ans and right_answers:
            display_true_ans = 1
        not_attempt_ans = 0
        if quiz.not_attempt_ans and not_attempt_answer:
            not_attempt_ans = 1
        message = ''
        is_message = 0
        for msg in quiz.quiz_message_ids:
            result_to = msg.result_to
            result_from = msg.result_from
            if (self.score <= result_to) and (self.score >= result_from):
                message = msg.message
                is_message = 1
        return {
            'wrong_answer': wrong_answers,
            'not_attempt_answer': not_attempt_answer,
            'right_answers': right_answers,
            'total_question': self.total_question,
            'total_correct': self.total_correct,
            'total_incorrect': self.total_incorrect,
            'total_marks': self.total_marks,
            'received_marks': self.received_marks,
            'percentage': "{:.2f}".format(self.score),
            'display_wrong_ans': display_wrong_ans,
            'display_true_ans': display_true_ans,
            'not_attempt_ans': not_attempt_ans,
            'message': message,
            'is_message': is_message,
            'user': self.env.user
        }

    def get_prev_next_result(self, line_id):
        self.ensure_one()
        next_result = False
        prev_result = False
        get_line_id = False
        question_no = 1
        if len(self.line_ids.ids) == 1:
            return {
                'next_result': False,
                'prev_result': False,
                'question_no': 1
            }
        line_no = {}
        current_que_no = 1
        if line_id:
            for line in self.line_ids:
                line_no.update({line.id: question_no})
                question_no += 1
                if get_line_id and not next_result:
                    next_result = line
                    continue
                elif get_line_id and next_result:
                    continue
                if line_id == line.id:
                    get_line_id = True
                else:
                    prev_result = line
            current_que_no = line_no[line_id]
        return {
            'next_result': next_result,
            'prev_result': prev_result,
            'question_no': current_que_no
        }

    @api.depends('quiz_id', 'quiz_id.categ_id')
    def _get_category(self):
        for obj in self:
            categ_id = False
            if obj.quiz_id and obj.quiz_id.categ_id:
                categ_id = obj.quiz_id.categ_id.id
            obj.categ_id = categ_id
        return True

    @api.depends('line_ids', 'line_ids.mark', 'line_ids.answer',
                 'line_ids.given_answer')
    def _get_result(self):
        for obj in self:
            obj.total_question = len(obj.line_ids.ids)
            total_correct = 0
            total_incorrect = 0
            total_not_attempt = 0
            total_marks = 0
            received_marks = 0
            for line in obj.line_ids:
                total_marks += line.question_mark or 0.0
                if not line.given_answer:
                    total_not_attempt += 1
                    continue
                if line.que_type == 'optional':
                    for answer in line.line_ids:
                        if answer.name == line.given_answer:
                            grade_val = answer.grade_id.value
                            received_mark = (
                                                    line.question_mark * grade_val) / 100
                            line.mark = received_mark
                            received_marks += received_mark
                            if answer.name == line.answer:
                                total_correct += 1
                            else:
                                total_incorrect += 1
                elif line.que_type == 'blank':
                    if line.case_sensitive:
                        if line.answer == line.given_answer:
                            received_mark = (
                                                    line.question_mark * (
                                                    line.grade_true_id.value or 0.0)) / 100
                            line.mark = received_mark
                            received_marks += received_mark
                            total_correct += 1
                        else:
                            received_mark = (
                                                    line.question_mark * (
                                                    line.grade_false_id.value or 0.0)) / 100
                            line.mark = received_mark
                            received_marks += received_mark
                            total_incorrect += 1
                    else:
                        if line.answer.lower() == line.given_answer.lower():
                            received_mark = (
                                                    line.question_mark * (
                                                    line.grade_true_id.value or 0.0)) / 100
                            line.mark = received_marks
                            received_marks += received_mark
                            total_correct += 1
                        else:
                            received_mark = (
                                                    line.question_mark * (
                                                    line.grade_false_id.value or 0.0)) / 100
                            line.mark = received_mark
                            received_marks += received_mark
                            total_incorrect += 1
                elif line.que_type == 'descriptive':
                    received_marks += line.mark
                    if line.mark > 0:
                        total_correct += 1
                    if line.mark == 0:
                        total_incorrect += 1
            obj.total_marks = total_marks or 0.0
            obj.total_not_attempt = total_not_attempt or 0.0
            obj.total_incorrect = total_incorrect or 0.0
            obj.total_correct = total_correct or 0.0
            obj.received_marks = received_marks or 0.0

            if received_marks != 0.0:

                obj.score = (received_marks * 100) / total_marks
            else:
                obj.score = 0.0
        return True

    name = fields.Char('Name')
    quiz_id = fields.Many2one('op.quiz', 'Quiz')
    categ_id = fields.Many2one(
        'op.quiz.category', 'Quiz Category', compute="_get_category",
        store=True)
    finish_date = fields.Datetime('Finished On')
    user_id = fields.Many2one('res.users', 'user')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    total_marks = fields.Float(compute="_get_result", store=True)
    received_marks = fields.Float(compute="_get_result", store=True)
    score = fields.Float('Score (%)', compute="_get_result", store=True)
    total_question = fields.Integer(
        'Total Question', compute="_get_result", store=True)
    total_correct = fields.Integer(
        'Total Correct', compute="_get_result", store=True)
    total_incorrect = fields.Integer(
        'Total Incorrect', compute="_get_result", store=True)
    total_not_attempt = fields.Float(
        'Total Not Attempt', compute="_get_result", store=True)
    line_ids = fields.One2many(
        'op.quiz.result.line', 'result_id', 'Result Line')
    state = fields.Selection([
        ('open', 'In-Progress'),
        ('hold', 'Hold'),
        ('submit', 'Submit'),
        ('asses', 'To Asses'),
        ('done', 'Done')], 'State')
    time_spent_hr = fields.Integer('Spent Hours')
    time_spent_minute = fields.Integer('Spent Minutes')
    time_spent_second = fields.Integer('Spent Seconds')
    company_id = fields.Many2one('res.company', string='Company')
    create_on = fields.Datetime('Create On', default=datetime.now())

    # @api.depends('line_ids', 'line_ids.mark', 'line_ids.answer',
    #              'line_ids.given_answer')
    # def _get_result(self):
    #     for obj in self:
    #         obj.total_question = len(obj.line_ids.ids)
    #         total_correct = 0
    #         total_incorrect = 0
    #         total_not_attempt = 0
    #         total_marks = 0
    #         received_marks = 0
    #         for line in obj.line_ids:
    #             total_marks += line.question_mark or 0.0
    #             total_correct += line.mark
    #             total_incorrect = obj.total_question - total_correct
    #             received_marks = total_correct
    #         obj.total_marks = total_marks or 0.0
    #         obj.total_not_attempt = total_not_attempt or 0.0
    #         obj.total_incorrect = total_incorrect or 0.0
    #         obj.total_correct = total_correct or 0.0
    #         obj.received_marks = received_marks or 0.0
    #         obj.score = (received_marks * 100) / total_marks
    #     return True

    def get_action_done(self):
        for obj in self:
            obj.state = 'done'
        return True

    def get_action_submit(self):
        for obj in self:
            obj.finish_date = fields.Datetime.now()
            obj.state = 'submit'
        return True

    def get_action_asses(self):
        for obj in self:
            obj.state = 'asses'
        return True


class OpQuizResultLine(models.Model):
    _name = "op.quiz.result.line"
    _description = "Quiz Result Line"

    name = fields.Html('Question')
    question_mark = fields.Float('Actual Marks')
    mark = fields.Float('Received Marks')
    answer = fields.Text('Correct Answer')
    que_type = fields.Selection([
        ('optional', 'Optional'), ('blank', 'Fill in the Blank'),
        ('descriptive', 'Descriptive')], 'Question Type', default='optional')
    grade_true_id = fields.Many2one(
        'op.answer.grade', 'Grade for truly given answer')
    grade_false_id = fields.Many2one(
        'op.answer.grade', 'Grade for wrongly given answer')
    case_sensitive = fields.Boolean('Case Sensitive')
    given_answer = fields.Text('User Answer')
    result_id = fields.Many2one('op.quiz.result', 'Result')
    line_ids = fields.One2many('op.quiz.result.line.answers',
                               'line_id', 'Answers')
    material_type = fields.Selection([('video', 'Video'),
                                      ('audio', 'Audio'),
                                      ('document', 'Document/PDF'),
                                      ('infographic', 'Image')], string='Material Type')
    document_url = fields.Char('Document URL')
    attachment_name = fields.Char('Attachment name')
    attachment = fields.Binary(attachment=True, string='Content')
    video_type = fields.Selection([('youtube', 'Youtube'),
                                   ('vimeo', 'Vimeo'),
                                   ('dartfish', 'Dartfish'),
                                   ('fileupload', 'FileUpload')], string='Video Type')


    @api.depends('name')
    def compute_display_name(self):
        for record in self:
            if record.name:
                display_name = BeautifulSoup(record.name).get_text()
                record.display_name = display_name

    def get_line_answer(self):
        self.ensure_one()
        given_answer_id = 0

        if self.given_answer:

            for line in self.line_ids:

                if line.name == self.given_answer:
                    given_answer_id = line.id

        return given_answer_id

    @api.onchange('mark')
    def _onchange_mark(self):
        if self.mark > self.question_mark:
            raise exceptions.ValidationError(
                _('Can not set more then actual mark.'))


class OpQuizResultLineAnswers(models.Model):
    _name = "op.quiz.result.line.answers"
    _description = "Quiz Result Line Answer"

    name = fields.Char('Answer', required=True)
    grade_id = fields.Many2one('op.answer.grade', 'Grade')
    line_id = fields.Many2one('op.quiz.result.line', 'Question')
