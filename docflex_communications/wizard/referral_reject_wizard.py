from odoo import models, fields, api, _

class DocflexReferralRejectWizard(models.TransientModel):
    _name = 'docflex.referral.reject.wizard'
    _description = 'معالج رفض الإحالة'
    
    referral_id = fields.Many2one('docflex.ticket.referral', required=True)
    rejection_reason = fields.Text(string='سبب الرفض', required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='مرفقات')
    
    def action_reject(self):
        self.ensure_one()
        # تحديث حالة الإحالة
        self.referral_id.write({
            'state': 'rejected',
            'response_date': fields.Datetime.now(),
            'response': self.rejection_reason
        })
        
        # إرفاق المستندات إذا وجدت
        if self.attachment_ids:
            self.referral_id.message_post(
                attachment_ids=self.attachment_ids.ids
            )
        
        # إرسال إشعار للمرسل
        self.referral_id.ticket_id.message_post(
            body=_("""<div style='margin:10px;'>
                <h3 style='color:#F44336;'>تم رفض الإحالة</h3>
                <p><b>السبب:</b> %s</p>
                <p><b>بواسطة:</b> %s</p>
                <p><b>التاريخ:</b> %s</p>
            </div>""") % (
                self.rejection_reason,
                self.env.user.name,
                fields.Datetime.now().strftime('%Y-%m-%d %H:%M')
            ),
            partner_ids=[self.referral_id.from_user_id.partner_id.id],
            subject=_("رفض الإحالة - %s") % self.referral_id.ticket_id.number
        )
        
        return {'type': 'ir.actions.act_window_close'}