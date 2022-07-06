# -*- coding: utf-8 -*-
#BY: LUIS FELIPE PATERNINA VITAL
from odoo import models, fields, api, _

class Area(models.Model):

    _name = "area"
    _inherit = 'mail.thread'
    _description = "Areas"

    
    name = fields.Char(string='Name', required=True, tracking=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)


    def _get_default_color(self):
        return randint(1, 11)

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
   