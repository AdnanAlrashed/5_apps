from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    department_id = fields.Many2one('hr.department', string='Department')
    is_department = fields.Boolean(string="Is Department")

    department_name = fields.Char(string='Department Name')
    # compute='_compute_ticket_count'
    ticket_count = fields.Integer("Tickets", )
    # sla_ids = fields.Many2many(
    #     'helpdesk.sla', 'helpdesk_sla_res_partner_rel',
    #     'res_partner_id', 'helpdesk_sla_id', string='SLA Policies',
    #     help="SLA Policies that will automatically apply to the tickets submitted by this customer.")

    # def _compute_ticket_count(self):
    #     all_partners_subquery = self.with_context(active_test=False)._search([('id', 'child_of', self.ids)])

    #     # group tickets by partner, and account for each partner in self
    #     groups = self.env['docflex.ticket']._read_group(
    #         [('partner_id', 'in', all_partners_subquery)],
    #         groupby=['partner_id'], aggregates=['__count'],
    #     )

    #     self.ticket_count = 0
    #     for partner, count in groups:
    #         while partner:
    #             if partner in self:
    #                 partner.ticket_count += count
    #             partner = partner.with_context(prefetch_fields=False).parent_id

    def action_open_docflex_ticket(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("docflex.docflex_ticket_action_main_tree")
        action.update({
            'domain': [('stage_id', 'in', self.ids)],
            'context': {
                'default_stage_id': self.id,
            },
        })
        return action
    
    # @api.model
    # def create(self, vals):
    #     # تحقق من إدخال اسم إدارة وإنشاء سجل إذا لم يكن موجوداً
    #     if not vals.get('department_id') and vals.get('department_name'):
    #         dept_name = vals['department_name']
    #         existing_department = self.search([('name', '=', dept_name), ('is_department', '=', True)], limit=1)
    #         if existing_department:
    #             vals['department_id'] = existing_department.id
    #         else:
    #             new_dept = self.create({
    #                 'name': dept_name,
    #                 'is_company': True,
    #                 'is_department': True,
    #             })
    #             vals['department_id'] = new_dept.id
    #     return super(ResPartner, self).create(vals)