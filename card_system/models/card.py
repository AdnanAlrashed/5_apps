from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
import qrcode
import logging

_logger = logging.getLogger(__name__)
class IDCard(models.Model):
    _name = 'id.card.card'
    _description = 'ID Card'

    citizen_id = fields.Many2one('id.card.citizen', string="Citizen", required=True)
    issue_date = fields.Date(string="Issue Date", required=True)
    expiry_date = fields.Date(string="Expiry Date", required=True)
    card_number = fields.Char(string="Card Number", readonly=True)
    status = fields.Selection([('active', 'Active'), ('expired', 'Expired')], string="Status", default="active")
    qr_code = fields.Image("QR Code", compute="_compute_qr_code", store=True)

    @api.model
    def create(self, vals):
        vals['card_number'] = self.env['ir.sequence'].next_by_code('id.card.card')
        print("from card",vals)
        return super().create(vals)

    @api.depends('citizen_id', 'card_number')
    def _compute_qr_code(self):
        for rec in self:
            if rec.citizen_id and rec.card_number:
                # نص رمز QR
                qr_text = f"citizen_id: {rec.citizen_id}\nNational ID: {rec.card_number}"
                _logger.info(f"QR content: {qr_text}")  # تتبع المحتوى داخل اللوج

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
