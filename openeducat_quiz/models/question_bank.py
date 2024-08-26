# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _


class OpQuestionBank(models.Model):
    _name = "op.question.bank"
    _description = "Quiz Question Bank"

    name = fields.Char('Name')
    bank_type_id = fields.Many2one('op.question.bank.type', 'Type')
    description = fields.Text('Description')
    line_ids = fields.One2many('op.question.bank.line', 'bank_id', 'Questions')

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for question bank'),
            'template': '/openeducat_quiz/static/xls/import_op_question_bank.xlsx'
        }]


class OpQuestionLine(models.Model):
    _name = "op.question.bank.line"
    _description = "Quiz Question Lines"

    name = fields.Html('Question')
    que_type = fields.Selection([
        ('optional', 'Optional'), ('blank', 'Fill in the Blank'),
        ('descriptive', 'Descriptive')], 'Question Type', default='optional')
    answer = fields.Char('Answer')
    grade_true_id = fields.Many2one(
        'op.answer.grade', 'Grade for truly given answer')
    grade_false_id = fields.Many2one(
        'op.answer.grade', 'Grade for wrongly given answer')
    bank_id = fields.Many2one('op.question.bank', 'Question Bank')
    case_sensitive = fields.Boolean('Case Sensitive')
    mark = fields.Float('Marks', default=1.0)
    line_ids = fields.One2many('op.question.bank.answer', 'question_id',
                               string='Question', copy=True)
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
    attachment = fields.Binary(attachment=True, string='Content')

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for question'),
            'template': '/openeducat_quiz/static/xls/nhap_cau_hoi.xls'
        }]


class OpQuesionBankAnswer(models.Model):
    _name = "op.question.bank.answer"
    _description = "Quiz Question Bank Answers"

    name = fields.Char('Answer')
    grade_id = fields.Many2one('op.answer.grade', 'Grade')
    question_id = fields.Many2one('op.question.bank.line', 'Question')


class OpQuestionBankType(models.Model):
    _name = "op.question.bank.type"
    _description = "Quiz Question Bank Type"

    name = fields.Char('Name')
    description = fields.Text('Description')
