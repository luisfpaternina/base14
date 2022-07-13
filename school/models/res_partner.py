# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import re
from datetime import date


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean(
        string="Is student")