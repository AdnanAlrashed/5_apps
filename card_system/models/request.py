# from odoo import models, fields

# class IDRequest(models.Model):
#     _name = 'id.card.request'
#     _description = 'ID Request'

#     citizen_id = fields.Many2one('id.card.citizen', string="Citizen", required=True)
#     request_date = fields.Date(string="Request Date", required=True)
#     status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='pending')

from odoo import models, fields

class IDCardRequest(models.Model):
    _name = 'id.card.request'
    _description = 'ID Card Request'

    citizen_id = fields.Many2one('id.card.citizen', string='Citizen', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('printed', 'Printed'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected')
    ], default='draft', string='State')
    request_date = fields.Date(string='Request Date', default=fields.Date.today)
    rejection_reason = fields.Text(string='Rejection Reason')
    branch_id = fields.Many2one('civil.branch', string='Issuing Branch')
