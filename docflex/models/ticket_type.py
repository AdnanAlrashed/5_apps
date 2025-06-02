from odoo import models, fields, _

class TicketType(models.Model):
    _name = 'ticket.type'
    _description = 'Ticket Type'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string='Code')
    serial_number = fields.Char(string='Serial Number')
    icon = fields.Image(string='Icon')
    active = fields.Boolean(_("نشط"), defualt=True)

    def name_get(self):
        return [(record.id, record.name) for record in self]
    