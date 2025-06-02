from odoo import models, fields
class Hostel1(models.Model):
 # …
    _name = 'hostel1.hostel1'
    _description = "Information about hostel1"

    email = fields.Char('Email')
    hostel_floors = fields.Integer(string="Total Floors")
    image = fields.Binary('Hostel Image')
    active = fields.Boolean("Active", default=True,
    help="Activate/Deactivate hostel record")
    type = fields.Selection(
        [
            ("male", "Boys"),
            ("female", "Girls"),
            ("common", "Common"),
        ], "Type", help="Type of Hostel",required=True, default="common")
    other_info = fields.Text("Other Information",
    help="Enter more information")
    description = fields.Html('Description')
    hostel_rating = fields.Float('Hostel Average Rating', 
    digits=(14, 4))