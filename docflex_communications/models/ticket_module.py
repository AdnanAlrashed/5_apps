from odoo import models ,fields, _


class TicketModule(models.Model):
  
    _name = 'ticket.module'
    _description = 'شاشة المذكرة  '
    name=fields.Char("الاسم")
    code=fields.Char("الرمز")
    is_default =  fields.Boolean("الافتراضية", defualt=True)
    icon = fields.Binary('الايقونة', attachment=True)

    color = fields.Integer()

class TicketModuleFields(models.Model):
  
    _name = 'ticket.module.fields'
    _description = 'حفول شاشة المذكرة  '
    name=fields.Char("الاسم")
    code=fields.Char("الرمز")

class TicketModuleFieldsData(models.Model):
  
    _name = 'ticket.module.fields.data'
    _description = 'بيانات شاشة المذكرة  '
    name=fields.Char("الاسم")
    code=fields.Char("الرمز")