from odoo import models, fields
class HostelRoomWizard(models.TransientModel):
    _name = 'hostel.room.wizard'
    _description = 'Hostel Room Wizard'

    name = fields.Char(string="Category Name")
    amount = fields.Float(string="Amount")
