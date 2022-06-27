from odoo import models, fields, api, _
from datetime import datetime, date
import logging


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    payment_mode_id = fields.Many2one(
        'account.payment.mode',
        string="Payment mode")
