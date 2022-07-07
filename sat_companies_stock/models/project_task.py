# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date


class ProjectTaks(models.Model):
    _inherit = 'project.task'

    product_id = fields.Many2one(
        'product.template',
        string="Gadget")
    is_conflictivea_pparatus = fields.Boolean(
        string="Is conflictive apparatus")


    @api.onchange('product_id')
    def onchange_recurrence_fields(self):
        self.recurring_task = False
        self.repeat_interval = False
        self.repeat_unit = False
        self.repeat_type = False
        self.mon = False
        self.tue = False
        self.wed = False
        self.thu = False
        self.fri = False
        self.sat = False
        self.sun = False
        if self.product_id and self.partner_id:
            product = self.product_id
            self.recurring_task = product.is_recurring_task
            self.repeat_interval = product.repeat_interval
            self.repeat_unit = product.repeat_unit
            self.repeat_type = product.repeat_type
            self.mon = product.mon
            self.tue = product.tue
            self.wed = product.wed
            self.thu = product.thu
            self.fri = product.fri
            self.sat = product.sat
            self.sun = product.sun
