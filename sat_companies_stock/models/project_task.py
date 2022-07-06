# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging


class ProjectTaks(models.Model):
    _inherit = 'project.task'

    is_conflictive_apparatus = fields.Boolean(
        string="Is conflictive apparatus",
        related="product_id.is_conflictive_apparatus")

    @api.model
    def create(self, vals):
        rec = super(ProjectTaks, self).create(vals)
        for record in rec:
            if record.product_id and record.partner_id:
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
        return rec
