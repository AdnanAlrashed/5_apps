from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#     res = super(DocFlexTicketStage, self).write(vals)
class DoflexTicket(models.Model):
    _inherit = 'docflex.ticket'
    
    # إضافة علاقات جديدة مع نظام المستندات
    attachment_number = fields.Integer(string="Attachment Number", compute='_compute_attachments')
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='المرفقات',
        relation='docflex_ticket_attachment_rel',  # تغيير اسم الجدول
        column1='docflex_ticket_id',              # تغيير اسم العمود
        column2='attachment_id',
        help='الملفات المرفقة مع التذكرة'
    )
    documents_folder_id = fields.Many2one(
        'documents.folder',
        string='مجلد المستندات',
        store=True,
        readonly=False,
        help='المجلد المخصص لحفظ مرفقات هذه التذكرة'
    )
    document_count = fields.Integer(
    string='عدد المستندات',
    compute='_compute_document_count',
    store=False
    )
    
    
    def _compute_document_count(self):
        Document = self.env['documents.document'].sudo()
        for record in self:
            record.document_count = Document.search_count([
                ('res_model', '=', 'docflex.ticket'),
                ('res_id', '=', record.id)
            ])


    def _compute_attachments(self):
        for ticket in self:
            ticket.attachment_number = len(ticket.attachment_ids)

    def open_attachments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'مرفقات التذكرة',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('res_id', '=', self.id), ('res_model', '=', 'docflex.ticket')],
            'context': {
                'default_res_model': 'docflex.ticket',
                'default_res_id': self.id,
            }
        }

    def _sync_documents(self):
        Document = self.env['documents.document'].sudo()
        existing_docs = Document.search_read([
            ('res_model', '=', 'docflex.ticket'),
            ('res_id', 'in', self.ids)
        ], fields=['attachment_id', 'res_id'])

        existing_map = {
            (doc['attachment_id'], doc['res_id']) for doc in existing_docs
        }

        for ticket in self:
            for attachment in ticket.attachment_ids:
                key = (attachment.id, ticket.id)
                if key not in existing_map:
                    Document.create({
                        'name': attachment.name,
                        'attachment_id': attachment.id,
                        'folder_id': ticket.documents_folder_id.id,
                        # 'owner_id': ticket.assing_to_id.id or self.env.user.id,
                        'res_model': 'docflex.ticket',
                        'res_id': ticket.id,
                    })

    @api.model
    def create(self, vals):

        if not vals.get('documents_folder_id'):
            parent_folder = self.env['documents.folder'].sudo().search([('name', '=', 'Docflex_Tickets')], limit=1)
            if not parent_folder:
                parent_folder = self.env['documents.folder'].sudo().create({'name': 'Docflex_Tickets'})
            folder = self.env['documents.folder'].sudo().create({
                'name': f"مرفقات التذكرة {vals.get('name', 'جديد')}",
                'company_id': vals.get('company_id') or self.env.company.id,
                'parent_folder_id': parent_folder.id,
            })
            vals['documents_folder_id'] = folder.id

        ticket = super(DoflexTicket, self).create(vals)

        # بعد إنشاء التذكرة، نقوم بمزامنة المستندات
        ticket._sync_documents()
        return ticket


    def write(self, vals):
        result = super(DoflexTicket, self).write(vals)
        for ticket in self:
            if not ticket.documents_folder_id:
                parent_folder = self.env['documents.folder'].sudo().search([('name', '=', 'Docflex_Tickets')], limit=1)
                if not parent_folder:
                    parent_folder = self.env['documents.folder'].sudo().create({'name': 'Docflex_Tickets'})
                folder = self.env['documents.folder'].sudo().create({
                    'name': f"مرفقات التذكرة {ticket.name or 'جديد'}",
                    'company_id': ticket.company_id.id,
                    'parent_folder_id': parent_folder.id,
                })
                ticket.documents_folder_id = folder
        self._sync_documents()
        return result

    def action_force_sync_documents(self):
        Document = self.env['documents.document'].sudo()
        Attachment = self.env['ir.attachment'].sudo()

        for ticket in self:
            # تأكد من وجود المجلد
            if not ticket.documents_folder_id:
                parent_folder = self.env['documents.folder'].sudo().search([('name', '=', 'Docflex_Tickets')], limit=1)
                if not parent_folder:
                    parent_folder = self.env['documents.folder'].sudo().create({'name': 'Docflex_Tickets'})
                folder = self.env['documents.folder'].sudo().create({
                    'name': f"مرفقات التذكرة {ticket.name or 'جديد'}",
                    'company_id': ticket.company_id.id,
                    'parent_folder_id': parent_folder.id,
                })
                ticket.documents_folder_id = folder

            # ابحث عن كل المرفقات المرتبطة بالتذكرة مباشرة
            attachments = Attachment.search([
                ('res_model', '=', 'docflex.ticket'),
                ('res_id', '=', ticket.id)
            ])

            for attachment in attachments:
                # تحقق هل لها مستند موجود مسبقًا
                existing_doc = Document.search([
                    ('attachment_id', '=', attachment.id),
                    ('res_model', '=', 'docflex.ticket'),
                    ('res_id', '=', ticket.id)
                ], limit=1)

                if not existing_doc:
                    Document.create({
                        'name': attachment.name,
                        'attachment_id': attachment.id,
                        'folder_id': ticket.documents_folder_id.id,
                        # 'owner_id': ticket.assing_to_id.id or self.env.user.id,
                        'res_model': 'docflex.ticket',
                        'res_id': ticket.id,
                    })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents Synced',
            'res_model': 'documents.document',
            'view_mode': 'kanban,tree,form',
            'domain': [('res_model', '=', 'docflex.ticket'), ('res_id', '=', self.ids)],
            'context': {
                'default_res_model': 'docflex.ticket',
                'default_res_id': self.ids,
            }
        }
