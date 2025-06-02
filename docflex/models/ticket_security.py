from odoo import models ,fields, _,api
from random import randint

class TicketSecurity(models.Model):
  
    _name = 'ticket.security'
    _description = _('درجات السرية')

    def _get_default_color(self):
        return randint(1, 11)
    
    name=fields.Char(_("الاسم"))
    code = fields.Selection([
        ('normal',_("عادي")),
        ('secret',_("سري")),
        ('very_secrt',_("سري للغاية")),
    ], default='normal', string=_("طبيعة السرية"))
    active = fields.Boolean(_("نشط"), defualt=True)
    is_default =  fields.Boolean(_("الافتراضية"), defualt=True)
    icon = fields.Binary(_('الايقونة'), attachment=True)
    color = fields.Integer(_('اللون'),default=_get_default_color)

    