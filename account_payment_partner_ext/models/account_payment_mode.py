from odoo import models, fields, api, _
from datetime import datetime, date
import logging


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'
