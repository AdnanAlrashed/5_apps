from odoo import models ,fields

class ReferralType(models.Model):
    _name = 'referral.type'
    _description = 'أنواع الإجراءات'
    
    name = fields.Char("الاسم", required=True)
    code = fields.Char("الرمز", required=True)
    active = fields.Boolean("نشط", default=True)
    is_default = fields.Boolean("الافتراضية", default=False)
    icon = fields.Binary("الأيقونة")
    color = fields.Integer("لون المؤشر")
    description = fields.Text("وصف النوع")
    default_deadline_days = fields.Integer("الموعد النهائي الافتراضي (أيام)")
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'يجب أن يكون رمز الإجراء فريدًا!'),
    ]


    