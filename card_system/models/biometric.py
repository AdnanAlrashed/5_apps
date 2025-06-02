from odoo import models, fields

class BiometricData(models.Model):
    _name = 'civil.biometric'
    _description = 'Biometric Data'

    citizen_id = fields.Many2one('id.card.citizen', string='Citizen', required=True)
    type = fields.Selection([
        ('fingerprint', 'Fingerprint'),
        ('iris', 'Iris'),
        ('signature', 'Signature')
    ], required=True)
    data = fields.Binary(string='Biometric File')
