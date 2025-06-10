from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class DocflexTicketReferral(models.Model):
    _name = 'docflex.ticket.referral'
    _description = 'إحالات المذكرات'
    _order = 'referral_date desc'

    # إضافة حقل نوع الإجراء
    referral_type_id = fields.Many2one(
        'referral.type',
        string='نوع الإجراء',
        required=True,
        default=lambda self: self._get_default_referral_type()
    )
    
    # تعديل الحقول الأخرى حسب الحاجة
    ticket_id = fields.Many2one('docflex.ticket', string='المذكرة', required=True, ondelete='cascade')
    referral_date = fields.Datetime(string='تاريخ الإحالة', default=fields.Datetime.now)
    from_user_id = fields.Many2one('res.users', string='من المستخدم', default=lambda self: self.env.user)
    to_user_id = fields.Many2one('res.users', string='إلى المستخدم', required=True)
    to_department_id = fields.Many2one('hr.department', string='إلى الإدارة')
    notes = fields.Text(string='ملاحظات الإحالة')
    state = fields.Selection([
        ('pending', 'قيد الانتظار'),
        ('received', 'تم الاستلام'),
        ('processed', 'تم المعالجة'),
        ('rejected', 'مرفوضة')
    ], string='حالة الإحالة', default='pending')
    deadline = fields.Date(string='موعد التسليم المتوقع')
    is_urgent = fields.Boolean(string='عاجل')
    response = fields.Text(string='رد على الإحالة')
    response_date = fields.Datetime(string='تاريخ الرد')

    # في ticket_referrals.py
    is_active_referral = fields.Boolean(
        string="إحالة نشطة",
        default=True,
        help="تبين إذا كانت هذه الإحالة تمنع التعديل على المذكرة"
    )

    # دالة للحصول على نوع الإجراء الافتراضي
    @api.model
    def _get_default_referral_type(self):
        default_type = self.env['referral.type'].search([('is_default', '=', True)], limit=1)
        return default_type.id if default_type else False

    # عند تغيير نوع الإجراء، تحديث الموعد النهائي
    @api.onchange('referral_type_id')
    def _onchange_referral_type(self):
        if self.referral_type_id and self.referral_type_id.default_deadline_days > 0:
            self.deadline = fields.Date.today() + timedelta(days=self.referral_type_id.default_deadline_days)