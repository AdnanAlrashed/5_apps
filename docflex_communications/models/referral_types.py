from odoo import models ,fields


class ReferralType(models.Model):
  
    name = 'referral.type'
    _description = 'انواع الاجراءات '
    name=fields.Char("الاسم")
    code=fields.Char("الرمز")
    
    active = fields.Boolean("Active", defualt=True)
    # Creating interactive Kanban cards
    is_default =  fields.Boolean("الافتراضية", defualt=True)
    icon = fields.models.ImageField(_("الايقونة"), upload_to=None, height_field=None, width_field=None, max_length=None)
    color = fields.Integer()


    