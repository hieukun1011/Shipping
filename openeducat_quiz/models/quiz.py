# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import logging
import random
from datetime import datetime

from odoo import models, fields, api, exceptions, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class OpQuizResultMessage(models.Model):
    _name = "op.quiz.result.message"
    _description = "Quiz Result Message"

    result_from = fields.Float('Result From (%)')
    result_to = fields.Float('Result To (%)')
    message = fields.Html('Message')
    quiz_id = fields.Many2one('op.quiz', 'Quiz')


class OpQuiz(models.Model):
    _name = "op.quiz"
    _inherit = ['mail.thread']
    _description = "Quiz"

    @api.depends('line_ids', 'line_ids.mark')
    def _get_total_marks(self):
        for obj in self:
            total = 0.0
            for line in obj.line_ids:
                total += line.mark or 0.0
            obj.total_marks = total

    name = fields.Char('Name')
    state = fields.Selection([
        ('draft', 'Draft'), ('open', 'In-Progress'), ('done', 'Done'),
        ('cancel', 'Cancel')], 'State', default="draft")
    categ_id = fields.Many2one('op.quiz.category', 'Category')
    line_ids = fields.One2many('op.quiz.line', 'quiz_id', 'Questions')
    quiz_message_ids = fields.One2many('op.quiz.result.message', 'quiz_id',
                                       string='Messages')
    total_marks = fields.Integer(compute="_get_total_marks",
                                 string='Total Marks', store=True)
    quiz_result_ids = fields.One2many('op.quiz.result', 'quiz_id', 'Quiz Result')
    user_ids = fields.Many2many(
        'res.users', compute='_compute_quiz_users',
        store=True, string='Users')
    start_date = fields.Datetime(string='Start date', default=datetime.now())
    end_date = fields.Datetime(string='End date')
    company_id = fields.Many2many('res.company', string='Company')
    # Result Configuration
    show_result = fields.Boolean('Display Result')
    right_ans = fields.Boolean('Display Right Answer')
    wrong_ans = fields.Boolean('Display Wrong Answer')
    not_attempt_ans = fields.Boolean('Display Not Attempted Answer')

    # Quiz Config with Question Bank
    quiz_config = fields.Selection([
        ('normal', 'Manual'),
        ('quiz_bank_selected', 'Quiz Bank with Selected Question'),
        ('quiz_bank_random', 'Quiz Bank with Random Quesiton')],
        'Configuration', default='normal')
    no_of_question = fields.Integer(
        'No of Question from each Question Bank', default=5)
    config_ids = fields.One2many('op.quiz.config', 'quiz_id',
                                 string='Configuration')

    # Configuration Part
    single_que = fields.Boolean('Single Question Per Page', default=True)
    prev_allow = fields.Boolean('Previous Question Allowed')
    prev_readonly = fields.Boolean('Only One Time Answer')
    no_of_attempt = fields.Integer('No of Attempt')
    que_required = fields.Boolean('All Question are Required')
    shuffle = fields.Boolean('Shuffle the Choices')

    # Timing Configuration
    time_config = fields.Boolean('Time Configuration')
    time_limit_hr = fields.Integer('Hour')
    time_limit_minute = fields.Integer('Minutes')
    time_expire = fields.Selection([
        ('auto_submit', 'Open attempts are submitted automatically'),
        ('grace_period', "There is a grace period when open attempts can be "
                         "submitted, but no more questions answered"),
        ('cancel', "Attempts must be submitted before time expires, "
                   "or they are not counted")], 'When Time Expires')
    grace_period = fields.Boolean('Grace Period')
    grace_period_hr = fields.Integer('Submission Grace Period')
    grace_period_minute = fields.Integer('Minutes')
    start_view = fields.Selection([
        ('audio', 'Audio'), ('video', 'Video'), ('html', 'HTML')],
        'Starting View', default="html")
    quiz_audio = fields.Binary('Audio File')
    binary_quiz_audio_name = fields.Char('Name quiz Audio')
    binary_quiz_video_name = fields.Char('Name quiz video')
    quiz_video = fields.Binary('Video File')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")
    quiz_html = fields.Html('HTML Content')
    description = fields.Text('Sort Description')
    challenge_ids = fields.Many2many(
        'gamification.challenge', string='Challenges')
    type = fields.Selection([
        ('all', 'Open for all'),
        ('student', 'Specific Student'),
        ('specific_course', 'Specific course'),
        ('specific_batch', 'Specific Batch'),
    ], string='Type', default='all')
    student_ids = fields.Many2many('op.student', string='Student')
    total_quiz_count = fields.Integer('Total quiz result', compute='calculate_total_result_quiz', store=True)
    course_ids = fields.Many2many('op.course', string='Courses')
    batch_ids = fields.Many2many('op.batch', string='Batches')
    is_public_result = fields.Boolean('Display results outside the portal')


    @api.depends('quiz_result_ids')
    def calculate_total_result_quiz(self):
        for record in self:
            record.total_quiz_count = len(record.quiz_result_ids)

    def action_open_quiz_result(self):
        self.ensure_one()
        tree_id = self.env.ref('openeducat_quiz.view_op_quiz_result_tree').id
        form_id = self.env.ref('openeducat_quiz.view_op_quiz_result_form').id
        return {
            'name': _("Quiz result"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'res_model': 'op.quiz.result',
            'domain': [('quiz_id', '=', self.id)],
            'context': {
                'quiz_id': self.id
            }
        }


    def action_confirm(self):
        for obj in self:
            count = self.env['op.quiz.line'].search_count(
                [('quiz_id', '=', obj.id), ('que_type', '=', 'descriptive')])
            if obj.show_result and count > 0:
                obj.show_result = False
            obj.state = 'open'
        return True

    def action_draft(self):
        for obj in self:
            obj.state = 'draft'
        return True

    def action_cancel(self):
        for obj in self:
            obj.state = 'cancel'
        return True

    def action_done(self):
        for obj in self:
            obj.state = 'done'
        return True

    def action_random_question(self):
        self.ensure_one()
        question_list = []
        if self.line_ids:
            for line in self.line_ids:
                line.unlink()
        que_bank_line = self.env['op.question.bank.line']
        for config in self.config_ids:
            bank = config.bank_id
            question_ids = que_bank_line.search(
                [('bank_id', '=', bank.id)]).ids
            random.shuffle(question_ids)
            if config.no_of_question and config.no_of_question > 0:
                question_ids = question_ids[:config.no_of_question]
            for question in que_bank_line.browse(question_ids):
                line_data = []
                correct_ans = ''
                values = {
                    'name': question.name,
                    'question_mark': question.mark or 0.0,
                }
                if question.que_type == 'optional':
                    for answer in question.line_ids:
                        if answer.grade_id and answer.grade_id.value == 100.0:
                            correct_ans = answer.name
                        line_data.append([0, False, {
                            'name': answer.name,
                            'grade_id': answer.grade_id and
                                        answer.grade_id.id or False
                        }])
                    if not line_data:
                        continue
                    values['line_ids'] = line_data
                elif question.que_type == 'blank':
                    correct_ans = question.answer or ''
                    values['grade_true_id'] = question.grade_true_id.id
                    values['grade_false_id'] = question.grade_false_id.id
                    values['que_type'] = question.que_type
                    values['case_sensitive'] = question.case_sensitive or False
                else:
                    values['que_type'] = question.que_type
                values['answer'] = correct_ans
                question_list.append([0, False, values])
        return question_list

    def get_result_id(self):
        self.ensure_one()
        result_pool = self.env['op.quiz.result'].sudo()
        open_result = result_pool.search([
            ('user_id', '=', self.env.uid),
            ('quiz_id', '=', self.id),
            ('state', '=', 'open')])
        if open_result:
            return open_result[0]
        result_id = result_pool.search([
            ('user_id', '=', self.env.uid),
            ('quiz_id', '=', self.id),
            ('state', '=', 'done')])
        total_attempt = len(result_id)
        allowed_attempt = self.no_of_attempt or 0.0
        if allowed_attempt and total_attempt >= allowed_attempt:
            raise exceptions.ValidationError(
                _('You are already reached maximum attempt of this exam'))
        user = self.env['res.users'].browse(self.env.uid)
        line_data = []
        if self.quiz_config in ('quiz_bank_selected', 'normal'):
            for line in self.line_ids:
                answer_data = []
                correct_ans = ''
                values = {
                    'name': line.name,
                    'question_mark': line.mark
                }
                if line.que_type == 'optional':
                    for answer in line.line_ids:
                        if answer.grade_id and answer.grade_id.value == 100.0:
                            correct_ans = answer.name
                        answer_data.append([0, False, {
                            'name': answer.name,
                            'grade_id': answer.grade_id and
                                        answer.grade_id.id or False
                        }])
                    values['line_ids'] = answer_data
                elif line.que_type == 'blank':
                    correct_ans = line.answer or ''
                    values['grade_true_id'] = line.grade_true_id.id or 0.0
                    values['grade_false_id'] = line.grade_false_id.id or 0.0
                    values['que_type'] = line.que_type
                    values['case_sensitive'] = line.case_sensitive or False
                elif line.que_type == 'descriptive':
                    values['que_type'] = line.que_type
                values['answer'] = correct_ans
                if line.material_type:
                    values['material_type'] = line.material_type
                    values['video_type'] = line.video_type
                    values['attachment'] = line.attachment
                    values['document_url'] = line.document_url
                line_data.append([0, False, values])
        elif self.quiz_config == 'quiz_bank_random':
            line_data = self.action_random_question()
        if user.id == 5:
            result_id = result_pool.create({
                'name': self.name + ' - ' + user.name,
                'quiz_id': self.id,
                'company_id': user.company_id.id,
                'line_ids': line_data,
                'state': 'open'
            })
        else:
            result_id = result_pool.create({
                'name': self.name,
                'quiz_id': self.id,
                'user_id': user.id,
                'company_id': user.company_id.id,
                'line_ids': line_data,
                'state': 'open'
            })
        for challenge in self.challenge_ids:
            self.env['gamification.goal'].sudo().search(
                [('challenge_id', '=', challenge.id),
                 ('user_id', '=', request.env.uid),
                 ('state', '!=', 'reached')]).sudo().update_goal()
            challenge.sudo()._check_challenge_reward()
        return result_id

    def view_quiz(self):
        self.ensure_one()
        quiz_url = request.httprequest.host_url + "quiz/rules/" + str(slug(
            self.get_result_id()))
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': quiz_url
        }

    def redirect_exam(self):
        return request.httprequest.host_url + "quiz/rules/" + str(slug(
            self.get_result_id()))

    def quiz_allow(self):
        self.ensure_one()
        result_id = self.env['op.quiz.result'].search([
            ('user_id', '=', self.env.uid), ('quiz_id', '=', self.id),
            ('state', '=', 'done')])
        total_attempt = len(result_id)
        allowed_attempt = self.no_of_attempt or 0.0
        allow = 1
        if allowed_attempt and total_attempt >= allowed_attempt:
            allow = 0
        return allow

    def unlink(self):
        for record in self:
            if record.create_uid.id != self.env.user.id:
                raise ValidationError('you cannot delete a record when you are not the creator of it')
        return super(OpQuiz, self).unlink()

    # require login
    auth_required = fields.Boolean('Login required',
                                   help="Users with a public link will be requested to login before taking part to the survey")


class OpQuizLine(models.Model):
    _name = "op.quiz.line"
    _description = "Questions"

    name = fields.Html('Question')
    que_type = fields.Selection([
        ('optional', 'Optional'), ('blank', 'Fill in the Blank'),
        ('descriptive', 'Descriptive')], 'Question Type', default='optional')
    answer = fields.Char('Answer')
    grade_true_id = fields.Many2one(
        'op.answer.grade', 'Grade for truly given answer')
    grade_false_id = fields.Many2one(
        'op.answer.grade', 'Grade for wrongly given answer')
    case_sensitive = fields.Boolean('Case Sensitive')
    line_ids = fields.One2many('op.quiz.answer', 'line_id', 'Answers')
    quiz_id = fields.Many2one('op.quiz', 'Quiz')
    mark = fields.Float('Marks', default=1.0)
    que_id = fields.Many2one('op.question.bank.line', 'question')
    material_type = fields.Selection([('video', 'Video'),
                                      ('audio', 'Audio'),
                                      ('document', 'Document/PDF'),
                                      ('infographic', 'Image')], string='Material Type')
    video_type = fields.Selection([('youtube', 'Youtube'),
                                   ('vimeo', 'Vimeo'),
                                   ('dartfish', 'Dartfish'),
                                   ('fileupload', 'FileUpload')], string='Video Type')
    document_url = fields.Char('Document URL')
    document_id = fields.Char('Document ID')
    attachment_name = fields.Char('Attachment name')
    attachment = fields.Binary(attachment=True, string='Content')

    _sql_constraints = [
        ('check_mark', 'check(mark > 0)',
         'Questions mark should be greater then 0')
    ]

    def write(self, vals):
        if vals.get('document_url'):
            vals['attachment'] = False
        elif vals.get('attachment'):
            vals['document_url'] = False
        res = super(OpQuizLine, self).write(vals)
        return res


class OpQuizAnswer(models.Model):
    _name = "op.quiz.answer"
    _description = "Quiz Answers"

    name = fields.Char('Answer')
    grade_id = fields.Many2one('op.answer.grade', 'Grade', required=True)
    line_id = fields.Many2one('op.quiz.line', 'Question')


class OpAnswerGrade(models.Model):
    _name = "op.answer.grade"
    _description = "Quiz Answer Grades"

    name = fields.Char('Name')
    value = fields.Float('Grade (%)')


class OpQuizConfig(models.Model):
    _name = "op.quiz.config"
    _description = "Quiz Configuration"

    quiz_id = fields.Many2one('op.quiz', 'Quiz')
    bank_id = fields.Many2one('op.question.bank', 'Question Bank')
    no_of_question = fields.Integer('Number of Question')

# class SlideChannel(models.Model):
#     _inherit = 'slide.channel'
#
#     quiz_ids = fields.One2many('op.quiz', 'slide_channel_id', string='Quiz')
