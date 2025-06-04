from odoo import models ,fields, _,api
from random import randint


class TicketStatus(models.Model):
  
    _name = 'ticket.status'
    _description =_('حالات المذكرة')
    def _get_default_color(self):
        return randint(1, 11)

    name=fields.Char(_("الاسم"))
    code = fields.Selection([
        ('execute',_("منفذة")),
        ('execute',_("منفذة")),
        ('on_execute',_("تحت التنفيذ")),
        ('rejected',_("مرفوض")),
    ], default='on_execute', string=_("طبيعة السرية"))
    active = fields.Boolean(_("نشط"), defualt=True)
    is_default =  fields.Boolean(_("الافتراضية"), defualt=True)
    icon = fields.Binary(_('الايقونة'), attachment=True)
    color = fields.Integer(_('اللون'),default=_get_default_color)

    
    