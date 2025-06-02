from odoo import models ,fields, _,api
from random import randint

class TicketSection(models.Model):
  
    _name = 'ticket.section'
    _description = _('افسام المذكرات')
    def _get_default_color(self):
        return randint(1, 11)
    name=fields.Char(_("الاسم"))
    code = fields.Selection([
        ('paper',_("بريد ورقي")),
        ('mail',_("بريد الكتروني")),
        ('fax',_("فاكس")),
        ('sms',_("رسائل")),
        ('other',_("اخرى")),
    ], default='paper', string=_("طبيعة القسم"))
    connected_with = fields.Selection([
        ('incoming',_("الصادر")),
        ('outing',_("الوراد")),
        ('both',_("كلاهما")),
        
    ], default='both', string=_("مرتبط مع"))
    serail_number = fields.Char(string=_("تسلسل القسم"))
    active = fields.Boolean(_("نشط"), defualt=True)
    icon = fields.Binary(_('الايقونة'), attachment=True)
    color = fields.Integer(_('اللون'),default=_get_default_color)

    
    