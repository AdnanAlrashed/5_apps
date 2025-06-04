from odoo import models ,fields,_


class TicketSummary(models.Model):
  
    _name = 'ticket.summary'
    _description = _('موجز المذكرة')
    name=fields.Char(_("الاسم"))
    code=fields.Char(_("الرمز"))
    ticket_section_id = fields.Many2one(
        string=_('قسم المذكرات'),
        comodel_name='ticket.section',
        ondelete='restrict',
    )
    
    active = fields.Boolean(_("نشط"), defualt=True)
   