from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
import qrcode


class Citizen(models.Model):
    _name = 'id.card.citizen'
    _description = 'Citizen Information'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']

    name = fields.Char(string="Full Name", required=True)
    birth_date = fields.Date(string="Date of Birth", required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    address = fields.Text(string="Address")
    national_id = fields.Char(string="National ID", readonly=True, copy=False)
    qr_code = fields.Image("QR Code", compute="_compute_qr_code", store=True)
    photo = fields.Binary(string="Photo")
    biometric_ids = fields.One2many('civil.biometric', 'citizen_id', string='Biometric Data')
    state = fields.Selection([('draft', 'Draft'), ('verified', 'Verified')], default='draft', string="Status")
    address = fields.Text(string='Permanent Address')
    current_address = fields.Text(string='Current Address')

    
    @api.model
    def create(self, vals):
        if not vals.get('national_id'):
            vals['national_id'] = self.env['ir.sequence'].next_by_code('id.card.citizen')
        return super(Citizen, self).create(vals)

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            duplicate = self.search([
                ('name', 'ilike', record.name),
                ('id', '!=', record.id)
            ], limit=1)
            if duplicate:
                raise ValidationError("The name '%s' is already used for another citizen (case-insensitive)." % record.name)

    @api.depends('name', 'national_id')
    def _compute_qr_code(self):
        for rec in self:
            if rec.name and rec.national_id:
                # نص رمز QR
                qr_text = f"Name: {rec.name}\nNational ID: {rec.national_id}"
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=5,
                    border=2,
                )
                qr.add_data(qr_text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                rec.qr_code = base64.b64encode(buffer.getvalue())
            else:
                rec.qr_code = False


# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
# import base64
# from io import BytesIO
# import qrcode
# import logging

# _logger = logging.getLogger(__name__)
# class Citizen(models.Model):
#     _name = 'id.card.citizen'
#     _description = 'Citizen Information'
#     # _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']

#     name = fields.Char(string='Full Name', required=True)
#     gender = fields.Selection([('male', 'Male'), ('female', 'Female')], required=True)
#     birth_date = fields.Date(string='Date of Birth', required=True)
#     birth_place = fields.Char(string='Place of Birth')
#     national_id = fields.Char(string='National ID', required=True, unique=True)
#     nationality = fields.Char(string='Nationality')
#     religion = fields.Char(string='Religion')
#     marital_status = fields.Selection([
#         ('single', 'Single'),
#         ('married', 'Married'),
#         ('divorced', 'Divorced'),
#         ('widowed', 'Widowed')
#     ])
#     photo = fields.Image(string='Photo')
#     qr_code = fields.Image("QR Code", compute="_compute_qr_code", store=True)
#     biometric_ids = fields.One2many('civil.biometric', 'citizen_id', string='Biometric Data')
#     address = fields.Text(string='Permanent Address')
#     current_address = fields.Text(string='Current Address')
