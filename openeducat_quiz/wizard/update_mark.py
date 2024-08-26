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


class OpUpdateMark(models.TransientModel):
    _name = "op.update.mark"
    _description = "Update Mark Wizard"

    name = fields.Text('Question')
    answer = fields.Text('Given Answer')
    mark = fields.Float('User Answer')

    def action_confirm_mark(self):
        self.ensure_one()
        line = self.env['op.quiz.result.line'].browse(
            self.env.context.get('active_id'))
        if self.mark > line.question_mark or self.mark < 0:
            raise exceptions.ValidationError(_('Set proper marks.'))
        else:
            line.mark = self.mark
