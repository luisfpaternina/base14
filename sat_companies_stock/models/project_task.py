# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging


class ProjectTaks(models.Model):
    _inherit = 'project.task'

    @api.onchange('product_id')
    def related_recurrence_fields(self):
        for record in self:
            if record.product_id:
                product = record.product_id
                record.recurring_task = product.is_recurring_task
                record.repeat_interval = product.repeat_interval
                record.repeat_unit = product.repeat_unit
                record.repeat_type = product.repeat_type
                record.mon = product.mon
                record.tue = product.tue
                record.wed = product.wed
                record.thu = product.thu
                record.fri = product.fri
                record.sat = product.sat
                record.sun = product.sun
            else:
                record.recurring_task = False
                record.repeat_interval = False
                record.repeat_unit = False
                record.repeat_type = False
                record.mon = False
                record.tue = False
                record.wed = False
                record.thu = False
                record.fri = False
                record.sat = False
                record.sun = False
