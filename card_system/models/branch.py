from odoo import models, fields

class BranchOffice(models.Model):
    _name = 'civil.branch'
    _description = 'Civil Office Branch'

    name = fields.Char(string='Branch Name', required=True)
    location = fields.Char(string='Location')
    manager_id = fields.Many2one('res.users', string='Branch Manager')
