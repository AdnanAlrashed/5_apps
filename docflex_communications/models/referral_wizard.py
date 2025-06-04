from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class DocflexTicketReferralWizard(models.TransientModel):
    _name = 'docflex.ticket.referral.wizard'
    _description = 'معالج إحالة المذكرة'

    # إضافة حقل نوع الإجراء
    referral_type_id = fields.Many2one(
        'referral.type',
        string='نوع الإجراء',
        required=True,
        default=lambda self: self._get_default_referral_type()
    )
    
    ticket_id = fields.Many2one('docflex.ticket', string='المذكرة', required=True)
    from_user_id = fields.Many2one('res.users', string='من المستخدم', required=True)
    to_user_id = fields.Many2one('res.users', string='إلى المستخدم')
    to_department_id = fields.Many2one('hr.department', string='إلى الإدارة')
    notes = fields.Text(string='ملاحظات الإحالة')
    deadline = fields.Date(string='موعد التسليم المتوقع')
    is_urgent = fields.Boolean(string='عاجل')

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

    @api.onchange('to_department_id')
    def _onchange_to_department(self):
        if self.to_department_id:
            return {'domain': {'to_user_id': [('department_id', '=', self.to_department_id.id)]}}
        return {'domain': {'to_user_id': []}}

    def action_refer(self):
        self.ensure_one()
        if not self.to_user_id and not self.to_department_id:
            raise UserError(_("يجب تحديد مستلم أو إدارة للمذكرة"))
        
        referral_vals = {
            'ticket_id': self.ticket_id.id,
            'referral_type_id': self.referral_type_id.id,
            'from_user_id': self.from_user_id.id,
            'to_user_id': self.to_user_id.id,
            'to_department_id': self.to_department_id.id,
            'notes': self.notes,
            'deadline': self.deadline,
            'is_urgent': self.is_urgent
        }
        
        referral = self.env['docflex.ticket.referral'].create(referral_vals)
        
        # إرسال إشعار للمستلم
        if self.to_user_id:
            self.ticket_id.message_subscribe(partner_ids=[self.to_user_id.partner_id.id])
            self.ticket_id.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.to_user_id.id,
                summary=_('إحالة مذكرة جديدة - %s') % self.referral_type_id.name,
                note=_('تم إحالة المذكرة %s إليك من %s\nنوع الإجراء: %s') % (
                    self.ticket_id.name, 
                    self.from_user_id.name,
                    self.referral_type_id.name
                )
            )
        
        self.ticket_id.message_post(
            body=_("تم إحالة المذكرة إلى %s (نوع الإجراء: %s)") % (
                self.to_user_id.name if self.to_user_id else self.to_department_id.name,
                self.referral_type_id.name
            )
        )
        
        return {'type': 'ir.actions.act_window_close'}