from odoo import models ,fields, _,api
from random import randint

class TicketClassification(models.Model):
  
    _name = 'ticket.classification'
    _description = _('تصنيف المذكرات')
    def _get_default_color(self):
        return randint(1, 11)
    name=fields.Char(_("الاسم"))
    active = fields.Boolean(_("نشط"), defualt=True)
    is_default =  fields.Boolean(_("الافتراضية"), defualt=True)
    icon = fields.Binary(_('الايقونة'), attachment=True)
    color = fields.Integer(_('اللون'),default=_get_default_color)


    