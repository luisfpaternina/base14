# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
import xlwt
import base64
import re
#from cStringIO import StringIO
from odoo.exceptions import UserError,ValidationError

class BimPurchaseRequisition(models.Model):
    _inherit = ['mail.thread']
    _description = "Material Request"
    _name = 'bim.purchase.requisition'
    _order = "id desc"

    @api.model
    def default_get(self, default_fields):
        values = super(BimPurchaseRequisition, self).default_get(default_fields)
        active_id = self._context.get('active_id')
        project = self.env['bim.project'].browse(active_id)
        values['warehouse_id'] = project.warehouse_id.id
        return values

    @api.model
    def _default_warehouse_id(self):
        active_id = self._context.get('active_id')
        project = self.env['bim.project'].browse(active_id)
        return project.warehouse_id.id

    name = fields.Char('Code', default="New")
    user_id = fields.Many2one('res.users', string='Responsable', tracking=True, default=lambda self: self.env.user)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company, required=True)
    date_begin = fields.Date('Start Date', default = lambda self: datetime.today())
    date_prevista = fields.Date('Expected date')
    project_id = fields.Many2one('bim.project', string='Project', domain="[('company_id','=',company_id)]")
    obs = fields.Text('Notes')
    warehouse_id = fields.Many2one('stock.warehouse','Warehouse', default=_default_warehouse_id)
    maintenance_id = fields.Many2one('bim.maintenance','Maintenance')
    analytic_id = fields.Many2one('account.analytic.account', 'Analytical Account')
    state = fields.Selection(
        [('nuevo', 'New'),
         ('aprobado', 'Approved'),
         ('finalizado', 'Done'),
         ('cancelled', 'Cancelled')],
        'Status', default='nuevo', tracking=True)
    product_ids = fields.One2many('product.list', 'requisition_id', string='Product List')
    picking_ids = fields.One2many('stock.picking', 'bim_requisition_id', string='Transfers')
    picking_count = fields.Integer('Quantity Transf', compute="_compute_picking")
    purchase_ids = fields.One2many('purchase.order', 'bim_requisition_id', string='Purchases')
    purchase_requisition_ids = fields.Many2many('purchase.requisition', string='Purchase Agreement')
    purchase_count = fields.Integer('Quantity Purchases', compute="_compute_purchases")
    agree_count = fields.Integer('Agreement Quantity', compute="_compute_purchase_requisitions")
    amount_total = fields.Float('Total', compute="_compute_total")
    space_id = fields.Many2one('bim.budget.space', 'Space')

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.analytic_id = self.project_id.analytic_id.id
        self.warehouse_id = self.project_id.warehouse_id.id

    def action_approve(self):
        self.write({'state': 'aprobado'})

    def action_done(self):
        self.write({'state': 'finalizado'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'new'})

    @api.model
    def create(self, vals):
        if vals.get('name', "New") == "New":
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.purchase.requisition') or "New"
        res = super(BimPurchaseRequisition, self).create(vals)
        if res.project_id:
            res.name += ' - ' + res.project_id.nombre
        return res

    def _compute_picking(self):
        for req in self:
            req.picking_count = len(req.picking_ids)

    def _compute_purchases(self):
        for req in self:
            req.purchase_count = len(req.purchase_ids)

    def _compute_purchase_requisitions(self):
        for req in self:
            req.agree_count = len(req.purchase_requisition_ids)

    def _compute_total(self):
        for record in self:
            record.amount_total = sum(pd.subtotal for pd in record.product_ids)

    def create_picking(self):
        if not self.project_id.stock_location_id:
            raise ValidationError(_('Project %s does not have an inventory location configured'%self.project_id.nombre))
        view_id = self.env.ref('stock.view_picking_form').id
        context = self._context.copy()
        context['default_bim_requisition_id'] = self.id
        picking_type = self.env['stock.picking.type'].search([('code','=','internal'),('warehouse_id','=',self.warehouse_id.id)], limit = 1)
        context['default_picking_type_id'] = picking_type.id
        context['default_bim_project_id'] = self.project_id.id if self.project_id else False
        context['default_picking_type_id'] = picking_type.id
        context['default_location_dest_id'] = self.project_id.stock_location_id.id
        return {
            'name': 'New',
            'view_mode': 'tree',
            'views': [(view_id,'form')],
            'res_model': 'stock.picking',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    def action_view_pickings(self):
        pickings = self.mapped('picking_ids')
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        if len(pickings) > 0:
            action['domain'] = [('id', 'in', pickings.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_purchases(self):
        purchases = self.mapped('purchase_ids')
        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        if len(purchases) > 0:
            action['domain'] = [('id', 'in', purchases.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_agreement(self):
        agreements = self.mapped('purchase_requisition_ids')
        action = self.env.ref('purchase_requisition.action_purchase_requisition').sudo().read()[0]
        if len(agreements) > 0:
            action['domain'] = [('id', 'in', agreements.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


    # def button_print_xls(self):
    #     self.ensure_one
    #     today = datetime.today().strftime("%d-%m-%Y")
    #     workbook = xlwt.Workbook(encoding="utf-8")
    #     style_title = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
    #     worksheet = workbook.add_sheet('Solicitudes de Materiales')
    #     k = 0
    #     j = 0
    #     worksheet.write_merge(k, k, j, j, 'Code', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Project', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Start Date', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Fecha Prevista', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Responsable', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Estado', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Code', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Product', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Etiquetas', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'U.M', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Quantity', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Coste', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Sub Total', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Despachado', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Notes', style_title);j += 1
    #     worksheet.write_merge(k, k, j, j, 'Realizado', style_title);j += 1
    #     row_index = 1
    #     for req in self:
    #         for req_prod in req.product_ids:
    #             j = 0
    #             tags = [x.name for x in req_prod.product_id.tag_ids]
    #             subtotal = req_prod.quant * req_prod.product_id.standard_price
    #             worksheet.write(row_index, j, req.name, );j += 1
    #             worksheet.write(row_index, j, req.project_id.nombre, );j += 1
    #             worksheet.write(row_index, j, req.date_begin, );j += 1
    #             worksheet.write(row_index, j, req.date_prevista, );j += 1
    #             worksheet.write(row_index, j, req.user_id.name, );j += 1
    #             worksheet.write(row_index, j, req.state, );j += 1
    #             worksheet.write(row_index, j, req_prod.product_id.default_code, );j += 1
    #             worksheet.write(row_index, j, req_prod.product_id.name, );j += 1
    #             worksheet.write(row_index, j, ','.join(tags), );j += 1
    #             worksheet.write(row_index, j, req_prod.product_id.uom_id.name, );j += 1
    #             worksheet.write(row_index, j, req_prod.quant, );j += 1
    #             worksheet.write(row_index, j, req_prod.product_id.standard_price, );j += 1
    #             worksheet.write(row_index, j, subtotal, );j += 1
    #             worksheet.write(row_index, j, req_prod.despachado, );j += 1
    #             worksheet.write(row_index, j, req_prod.Notes, );j += 1
    #             worksheet.write(row_index, j, req_prod.realizado, );j += 1
    #             row_index += 1
    #     fp = StringIO()
    #     workbook.save(fp)
    #     fp.seek(0)
    #     data = fp.read()
    #     fp.close()
    #     data_b64 = base64.encodebytes(data)
    #     doc = self.env['ir.attachment'].create({
    #         'name': 'Detalle Solicitudes Materiales %s.xls'%today,
    #         'datas': data_b64,
    #         'datas_fname': 'Detalle Solicitudes Materiales %s.xls'%today,
    #     })
    #     return {
    #             'type' : "ir.actions.act_url",
    #             'url': "web/content/?model=ir.attachment&id="+str(doc.id)+"&filename_field=datas_fname&field=datas&download=true&filename="+str(doc.name),
    #             'target': "self",
    #             'no_destroy': False,
    #     }

class ProductList(models.Model):
    _name = 'product.list'
    _description = 'Product List'
    _rec_name = 'product_id'

    solo_lectura = fields.Boolean('Readonly', default=False, compute='_compute_giveme_state')

    def _compute_giveme_state(self):
        if self.requisition_id.state == 'new':
            self.solo_lectura = False
        else:
            self.solo_lectura = True

    @api.depends('requisition_id.picking_ids')
    def _compute_qty_done(self):
        for record in self:
            moves = record.requisition_id.picking_ids.mapped('move_lines').filtered(lambda m: m.state == 'done' and m.product_id.id == record.product_id.id)
            record.qty_done = sum(x.product_uom_qty for x in moves)

    @api.depends('qty_done','quant')
    def _compute_qty_to_process(self):
        for record in self:
            record.qty_to_process = record.quant - record.qty_done
            record.subtotal = record.quant * record.cost

    @api.depends('requisition_id.purchase_ids')
    def _compute_qty_purchase(self):
        for record in self:
            purchase_lines = record.requisition_id.purchase_ids.mapped('order_line').filtered(lambda r: r.bim_req_line_id.id == record.id and r.state != 'cancel')
            record.qty_purchase = sum(x.product_qty for x in purchase_lines)

    product_id = fields.Many2one('product.product', 'Product')
    quant = fields.Float('Quantity')
    cost = fields.Float('Cost')
    subtotal = fields.Float('Subtotal', compute="_compute_qty_to_process")
    despachado = fields.Float('Dispatched')
    obs = fields.Text('Notes')
    um_id = fields.Many2one('uom.uom', 'U.M')
    done = fields.Boolean('Done')
    qty_to_process = fields.Float('To process', compute="_compute_qty_to_process")
    qty_done = fields.Float('Dispatched Quant.', compute="_compute_qty_done")
    qty_purchase = fields.Float('Purchased', compute="_compute_qty_purchase")
    sent_to_production = fields.Boolean('Sent to production')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company, required=True)
    analytic_id = fields.Many2one('account.analytic.account', 'Analytical account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytical Tags')
    partner_ids = fields.Many2many('res.partner', string='Supplier')
    #partner_id = fields.Many2one('res.partner','Supplier')
    requisition_id = fields.Many2one('bim.purchase.requisition', 'Requisition', ondelete='cascade')
    project_id = fields.Many2one('bim.project', string="Project", domain="[('company_id','=',company_id)]")

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.um_id = self.product_id.uom_id.id
        self.analytic_id = self.requisition_id.analytic_id.id
        self.project_id = self.requisition_id.project_id.id
        self.cost = self.product_id.standard_price

    @api.constrains('product_id')
    def _check_product_id(self):
        if not self.requisition_id.state == 'nuevo':
            raise ValidationError(_("You cannot Add Lines in this State"))

    def unlink(self):
        for requisition_list in self:
            if requisition_list.solo_lectura:
                raise UserError(_('You cannot delete a Line in this other than New!'))
        return super(ProductList, self).unlink()

