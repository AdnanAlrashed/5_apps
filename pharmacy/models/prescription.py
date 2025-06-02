from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'  # توريث النموذج الأساسي للشركاء
    
    # الحقول الجديدة
    is_doctor = fields.Boolean(
        string="Doctor",
        help="تحديد إذا كان هذا الشخص طبيباً معتمداً في النظام",
        default=False
    )
    
    is_patient = fields.Boolean(
        string="Patient", 
        help="تحديد إذا كان هذا الشخص مريضاً في النظام",
        default=False
    )
    
    # إضافة قيود للتأكد من عدم تحديد كلا الخيارين معاً
    @api.constrains('is_doctor', 'is_patient')
    def _check_roles(self):
        for partner in self:
            if partner.is_doctor and partner.is_patient:
                raise ValidationError("لا يمكن أن يكون الشخص طبيباً ومريضاً في نفس الوقت!")
            
class Prescription(models.Model):
    _name = 'pharmacy.prescription'
    _description = 'Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # الحقول مع تتبع التغييرات
    name = fields.Char(
        string="Prescription Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', tracking=True)
    
    doctor_id = fields.Many2one(
        'res.partner',
        string="Doctor",
        domain=[('is_doctor', '=', True)],
        tracking=True
    )
    
    # حقل مع شرط visibility جديد بدلاً من attrs
    patient_id = fields.Many2one(
        'res.partner',
        string="Patient",
        domain=[('is_patient', '=', True)],
        tracking=True,
        # readonly="state in ['done', 'canceled']"  # بديل states
    )
    
    date = fields.Date(
        string="Date",
        default=fields.Date.context_today,
        tracking=True
    )
    
    note = fields.Html(string="Notes")
    picking_id = fields.Many2one('stock.picking', string="Delivery Order", readonly=True)
    force_override = fields.Boolean(
        string="Force Override",
        help="Allow saving even if stock is insufficient",
        readonly="state != 'draft'"  # بديل states
    )
    
    # حقل محسوب مع إمكانية التخزين لتحسين الأداء
    show_stock_warning = fields.Boolean(
        string="Show Stock Warning",
        compute="_compute_show_stock_warning",
        store=True
    )
    
    line_ids = fields.One2many(
        'pharmacy.prescription.line',
        'prescription_id',
        string="Medicines",
        readonly="state in ['done', 'canceled']"  # بديل states
    )

    @api.depends('line_ids.product_id', 'line_ids.quantity')
    def _compute_show_stock_warning(self):
        for prescription in self:
            prescription.show_stock_warning = any(
                line.product_id and 
                (line.product_id.qty_available <= 0 or 
                 line.quantity > line.product_id.qty_available)
                for line in prescription.line_ids
            )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pharmacy.prescription') or _('New')
        return super().create(vals)

    # طرق تغيير الحالة
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'canceled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})



class PrescriptionLine(models.Model):
    _name = 'pharmacy.prescription.line'
    _description = 'Prescription Line'
    _order = 'id asc'

    prescription_id = fields.Many2one(
        'pharmacy.prescription',
        string="Prescription",
        required=True,
        ondelete="cascade"
    )
    
    product_id = fields.Many2one(
        'product.product',
        string="Medicine",
        required=True,
        domain=[('type', '=', 'product')]
    )
    
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
        digits='Product Unit of Measure'
    )
    
    available_qty = fields.Float(
        string="Available Quantity",
        compute="_compute_available_qty",
        digits='Product Unit of Measure'
    )

    @api.depends('product_id')
    def _compute_available_qty(self):
        for line in self:
            line.available_qty = line.product_id.qty_available if line.product_id else 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id:
                continue
                
            line.available_qty = line.product_id.qty_available
            
            if line.product_id.qty_available <= 0:
                return {
                    'warning': {
                        'title': _("Stock Warning"),
                        'message': _("This product is out of stock.")
                    }
                }

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("Quantity must be positive."))