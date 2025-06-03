from odoo import models , fields, api ,Command, _
from odoo.exceptions import ValidationError, UserError
class DoflexTicket(models.Model):
    _name = 'docflex.ticket'
    # _inherit="helpdesk.ticket"
    _inherit = [
        'portal.mixin',
        'mail.thread.cc',
        'utm.mixin',
        'rating.mixin',
        'mail.activity.mixin',
        'mail.tracking.duration.mixin',
    ]
    
  
    _description = 'المذكرات'
    _track_duration_field = 'stage_id'
#     _sql_constraints = [
#     ('number_unique', 'UNIQUE(number)', 'الرقم التسلسلي يجب أن يكون فريدًا!'),
# ]

    _order = 'ticket_date desc, id desc'
    _rec_name = 'number'
    _check_company_auto = True

    
    
    name = fields.Char(string='الموضوع', required=True, index=True, tracking=True)

    number = fields.Char(
        string='الرقم التسلسلي',
        required=True,
        readonly=True,
        default=lambda self: _('New'),
        copy=False
    )
    referrenc_number=fields.Char("رقم المرجع ")
    topic=fields.Text("البيان")
    note=fields.Text("الملاحظة")
    partner_number=fields.Char("رقم الجهة")
    ticket_date = fields.Datetime(
        string='تاريخ المذكرة',
        default=fields.Datetime.now,
    )
    partner_from_id = fields.Many2one(
        string='من الجهة',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    partner_to_id = fields.Many2one(
        string='الى الجهة',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    folder_id= fields.Many2one(
        string='مساحة العمل',
        comodel_name='documents.folder',
        ondelete='restrict',
    )

    
    ticket_section_id = fields.Many2one(
        'ticket.section',
        string='قسم المذكرة',
        ondelete='restrict',
    )
    ticket_priority_id = fields.Many2one(
        string='درجة الاولوية ',
        comodel_name='ticket.priority',
        ondelete='restrict',
    )
    ticket_security_id = fields.Many2one(
        string='درجة السرية',
        comodel_name='ticket.security',
        ondelete='restrict',
    )
    ticket_type = fields.Many2one('ticket.type', string="Ticket Type", 
                                default=lambda self: self._get_default_ticket_type())
    ticket_status_id = fields.Many2one(
        string='حالة المذكرة',
        comodel_name='ticket.status',
        ondelete='restrict',
    )
    ticket_summary_id = fields.Many2one(
        string='الموجز',
        comodel_name='ticket.summary',
        ondelete='restrict',
    )
    
    ticket_classification_id = fields.Many2one(
        string='تصنيف المذكرة ',
        comodel_name='ticket.classification',
        ondelete='restrict',
    )
    stage_id = fields.Many2one(
        'docflex.ticket.stage', string='المرحلة',
        store=True,
        ondelete='restrict',
        tracking=1,
        copy=False, index=True
    )
    fold = fields.Boolean(related="stage_id.fold")
    wait_archive = fields.Boolean(
        string='wait archive',
    )
    
    archive = fields.Boolean(
        string='archive',
    )
    active = fields.Boolean(default=True)
    domain_user_ids = fields.Many2many('res.users', compute='_compute_domain_user_ids')
    is_partner_email_update = fields.Boolean('Partner Email will Update', compute='_compute_is_partner_email_update')
    is_partner_phone_update = fields.Boolean('Partner Phone will Update', compute='_compute_is_partner_phone_update')
    partner_name = fields.Char(string='Customer Name', compute='_compute_partner_name', store=True, readonly=False)
    partner_email = fields.Char(string='Customer Email', compute='_compute_partner_email', inverse="_inverse_partner_email", store=True, readonly=False)
    partner_phone = fields.Char(string='Customer Phone', compute='_compute_partner_phone', inverse="_inverse_partner_phone", store=True, readonly=False)
    commercial_partner_from_id = fields.Many2one(related="partner_from_id.commercial_partner_id")
    closed_by_partner = fields.Boolean('Closed by Partner', readonly=True)
    tag_ids = fields.Many2many('docflex.tag', string='Tags')
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
        required=True,
        ondelete='restrict',
        tracking=True,
        readonly=True,  # Make it readonly to prevent changes from the form view
        domain="[('id', 'in', [company_id.id])]"  # Ensure it only shows the current company
        )
    department_id = fields.Many2one('hr.department', string='User Department', readonly=True)
    user_id = fields.Many2one('res.users', string='Created by User', readonly=True)
    user_name = fields.Char(string="User Name", readonly=True)
    color = fields.Integer(string='Color Index')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', tracking=True)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    
    ticket_type_code = fields.Char(related='ticket_type.code', store=True)
    ticket_section_code = fields.Selection(related='ticket_section_id.code', store=True)
    sequence_year = fields.Char(compute='_compute_sequence_year', store=True)

    # إضافة هذه الحقول في نموذج docflex.ticket
    ticket_date_date = fields.Date(
        string="تاريخ المذكرة (تاريخ فقط)",
        compute='_compute_ticket_date_date',
        store=True,
        index=True
    )

    sequence_year = fields.Char(
        string="سنة التسلسل",
        compute='_compute_sequence_year',
        store=True,
        index=True
    )

    ticket_month = fields.Char(string="شهر التذكرة", compute="_compute_ticket_month", store=True)
    ticket_week = fields.Char(string="أسبوع التذكرة", compute="_compute_ticket_week", store=True)

    ticket_count = fields.Integer(string="عدد التذاكر", default=1, help="يُستخدم للعد في عرض Pivot")


    is_today = fields.Boolean(compute="_compute_date_flags", store=True)
    is_this_week = fields.Boolean(compute="_compute_date_flags", store=True)
    is_this_month = fields.Boolean(compute="_compute_date_flags", store=True)


    request_archive_by = fields.Many2one('res.users', string="طلب الأرشفة بواسطة", readonly=True)
    request_archive_date = fields.Datetime(string="تاريخ طلب الأرشفة", readonly=True)

    archive_date = fields.Datetime(string="تاريخ الأرشفة", readonly=True)
    restored_date = fields.Datetime(string="تاريخ الاسترجاع", readonly=True)
    restored_by = fields.Many2one('res.users', string="تم الاسترجاع بواسطة", readonly=True)

    @api.depends('stage_id')
    def _compute_is_archived(self):
        for record in self:
            record.is_archived = record.stage_id.code in ['archiving', 'archived'] if record.stage_id else False

    is_archived = fields.Boolean(compute='_compute_is_archived', store=True, string="Is Archived")

    @api.constrains('stage_id')
    def _check_stage_transition(self):
        for rec in self:
            if rec.wait_archive and rec.stage_id:
                allowed_codes = ['archiving', 'archived']
                if rec.stage_id.code not in allowed_codes:
                    raise ValidationError(_("لا يمكن تغيير مرحلة مذكرة بانتظار الأرشفة إلا إلى 'مؤرشف'."))
    
    # def write(self, vals):
    #     for ticket in self:
    #         stage_code = ticket.stage_id.code if ticket.stage_id else False

    #         # الحالات المسموح بها لتعديل المذكرة في مراحل الأرشفة:
    #         is_unarchiving = (
    #             self.env.context.get('allow_unarchive') and
    #             vals.get('active') is True and
    #             'stage_id' in vals
    #         )

    #         is_requesting_archive = (
    #             self.env.context.get('request_archive') and
    #             vals.get('wait_archive') is True and
    #             'stage_id' in vals
    #         )

    #         is_archiving = (
    #             self.env.context.get('do_archive') and
    #             vals.get('active') is False and
    #             vals.get('wait_archive') is False  # تأكد أن wait_archive يتم تعطيله
    #         )

    #         # لا تمنع التعديل إذا كانت المذكرة في مرحلة "انتظار الأرشفة" (archiving) 
    #         # ويتم تنفيذ عملية أرشفة فعلية (is_archiving = True)
    #         if stage_code == 'archived' and not (is_unarchiving or is_requesting_archive or is_archiving):
    #             raise ValidationError(_("لا يمكن تعديل المذكرة المؤرشفة إلا عند الاسترجاع."))
            
    #         if stage_code == 'archiving' and not (is_requesting_archive or is_archiving):
    #             raise ValidationError(_("لا يمكن تعديل المذكرة في انتظار الأرشفة إلا عند تنفيذ الأرشفة أو إلغاء الطلب."))

    #         result = super().write(vals)

    #         # تحديث المرحلة إلى "مؤرشف" إذا تم تعطيل المذكرة
    #         if 'active' in vals and vals['active'] is False:
    #             archived_stage = self.env['docflex.ticket.stage'].search([('code', '=', 'archived')], limit=1)
    #             if archived_stage:
    #                 super(DoflexTicket, self).write({'stage_id': archived_stage.id})

    #     return result

    def write(self, vals):
        for ticket in self:
            stage_code = ticket.stage_id.code if ticket.stage_id else False

            # الحالات المسموح بها لتعديل المذكرة في مراحل الأرشفة:
            is_unarchiving = (
                self.env.context.get('allow_unarchive') and
                vals.get('active') is True and
                'stage_id' in vals
            )

            is_requesting_archive = (
                self.env.context.get('request_archive') and
                vals.get('wait_archive') is True and
                'stage_id' in vals
            )

            is_archiving = (
                self.env.context.get('do_archive') and
                vals.get('active') is False and
                vals.get('wait_archive') is False
            )

            is_canceling_archive = (
                self.env.context.get('cancel_archive') and
                vals.get('wait_archive') is False
            )

            # لا تمنع التعديل إذا كانت المذكرة في مرحلة "انتظار الأرشفة" (archiving) 
            # ويتم تنفيذ عملية أرشفة فعلية أو إلغاء
            if stage_code == 'archived' and not (is_unarchiving or is_requesting_archive or is_archiving or is_canceling_archive):
                raise ValidationError(_("لا يمكن تعديل المذكرة المؤرشفة إلا عند الاسترجاع."))
            
            if stage_code == 'archiving' and not (is_requesting_archive or is_archiving or is_canceling_archive):
                raise ValidationError(_("لا يمكن تعديل المذكرة في انتظار الأرشفة إلا عند تنفيذ الأرشفة أو إلغاء الطلب."))

            result = super().write(vals)

            # تحديث المرحلة إلى "مؤرشف" إذا تم تعطيل المذكرة
            if 'active' in vals and vals['active'] is False:
                archived_stage = self.env['docflex.ticket.stage'].search([('code', '=', 'archived')], limit=1)
                if archived_stage:
                    super(DoflexTicket, self).write({'stage_id': archived_stage.id})

        return result
    
    @api.depends('ticket_date')
    def _compute_date_flags(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_today = rec.ticket_date.date() == today if rec.ticket_date else False
            rec.is_this_week = rec.ticket_date.isocalendar()[1] == today.isocalendar()[1] if rec.ticket_date else False
            rec.is_this_month = rec.ticket_date.month == today.month and rec.ticket_date.year == today.year if rec.ticket_date else False

    @api.model
    def _get_default_stages(self):
        """Create default stages including archive-related stages"""
        stages = self.search([])
        if not stages:
            # Create basic stages if none exist
            stage_vals = [
                {
                    'name': 'جديد',
                    'sequence': 1,
                    'legend_normal': 'قيد المعالجة',
                    'legend_blocked': 'معلق',
                    'legend_done': 'مكتمل',
                },
                {
                    'name': 'جاري الأرشفة',
                    'sequence': 90,
                    'legend_normal': 'في انتظار الموافقة',
                    'legend_blocked': 'مرفوض',
                    'legend_done': 'تمت الموافقة',
                },
                {
                    'name': 'مؤرشف',
                    'sequence': 100,
                    'fold': True,
                    'legend_normal': 'يمكن استرجاعه',
                    'legend_blocked': 'محذوف',
                    'legend_done': 'مؤرشف',
                }
            ]
            for vals in stage_vals:
                self.create(vals)
        return stages


    def action_mark_waiting_archive(self):
        """زر لطلب أرشفة المذكرة"""

        waiting_stage = self.env['docflex.ticket.stage'].search(
            [('code', '=', 'archiving')],  # تأكد أن المرحلة لها code ثابت = archiving
            limit=1
        )

        for ticket in self:
            if not waiting_stage:
                raise ValidationError(_("لم يتم العثور على مرحلة 'جاري الأرشفة'. تأكد من وجودها."))

            ticket.with_context(request_archive=True).write({
                'stage_id': waiting_stage.id,
                'wait_archive': True,
                'request_archive_by': self.env.user.id,
                'request_archive_date': fields.Datetime.now(),
            })

            # سجل في المحادثات
            ticket.message_post(
                body=_("📦 تم طلب أرشفة المذكرة من قبل: <b>%s</b> في <i>%s</i>") % (
                    ticket.request_archive_by.name,
                    ticket.request_archive_date.strftime('%Y-%m-%d %H:%M')
                )
            )

            # إرسال تنبيه إلى مدير القسم
            if ticket.department_id and ticket.department_id.manager_id and ticket.department_id.manager_id.user_id:
                manager_user = ticket.department_id.manager_id.user_id
                ticket.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=manager_user.id,
                    summary='طلب أرشفة جديد',
                    note=_("""\
                        <div style='margin:10px;'>
                            <h3 style='color:#875A7B;'>طلب أرشفة جديد</h3>
                            <p><b>المستخدم:</b> %s</p>
                            <p><b>رقم المذكرة:</b> %s</p>
                            <p><b>موضوع المذكرة:</b> %s</p>
                            <p><b>تاريخ الطلب:</b> %s</p>
                        </div>
                    """) % (
                        ticket.request_archive_by.name,
                        ticket.number,
                        ticket.name,
                        ticket.request_archive_date.strftime('%Y-%m-%d %H:%M')
                    )
                )

    def action_cancel_archive_request(self):
        """إلغاء طلب الأرشفة وإعادة المذكرة إلى المرحلة السابقة"""
        for ticket in self:
            if not ticket.wait_archive:
                raise UserError(_("هذه المذكرة ليست في حالة انتظار أرشفة."))
            
            # البحث عن المرحلة السابقة (يمكن تعديل هذا المنطق حسب احتياجاتك)
            previous_stage = self.env['docflex.ticket.stage'].search([
                ('sequence', '<', ticket.stage_id.sequence),
                ('code', 'not in', ['archiving', 'archived'])
            ], order='sequence desc', limit=1)
            
            if not previous_stage:
                previous_stage = self.env['docflex.ticket.stage'].search([
                    ('is_starting', '=', True)
                ], limit=1)
            
            ticket.with_context(cancel_archive=True).write({
                'stage_id': previous_stage.id if previous_stage else ticket.stage_id.id,
                'wait_archive': False,
                'request_archive_by': False,
                'request_archive_date': False,
            })

            # تسجيل في المحادثات
            ticket.message_post(
                body=_("❌ تم إلغاء طلب الأرشفة بواسطة: <b>%s</b> في <i>%s</i>") % (
                    self.env.user.name,
                    fields.Datetime.now().strftime('%Y-%m-%d %H:%M')
                )
            )

    def action_archive(self):
        archived_stage = self.env['docflex.ticket.stage'].search(
            [('code', '=', 'archived')], 
            limit=1
        )
        if not archived_stage:
            raise ValidationError(_("لم يتم العثور على مرحلة 'مؤرشف'. تأكد من أن لها الكود: archived"))

        # استخدم super() لتجاوز أي قيود في write()
        super(DoflexTicket, self).with_context(do_archive=True).write({
            'stage_id': archived_stage.id,
            'active': False,
            'wait_archive': False,  # تأكد من تعطيل انتظار الأرشفة
            'archive_date': fields.Datetime.now(),
        })

        self.message_post(
            body=_("✅ تمت أرشفة المذكرة بواسطة: <b>%s</b> في <i>%s</i>") % (
                self.env.user.name,
                fields.Datetime.now().strftime('%Y-%m-%d %H:%M')
            )
        )

    def action_unarchive(self):
        """استرجاع المذكرة من الأرشيف وتعيين المرحلة إلى جديدة"""
        new_stage = self.env['docflex.ticket.stage'].search([('code', '=', 'new')], limit=1)

        if not new_stage:
            raise UserError(_("لا يمكن الاسترجاع لأن المرحلة (جديدة) غير معرفة. تأكد من أن لها الكود: new"))

        for ticket in self:
            if ticket.active:
                raise UserError(_("المذكرة بالفعل غير مؤرشفة."))

            ticket.with_context(allow_unarchive=True).write({
                'stage_id': new_stage.id,
                'active': True,
                'wait_archive': False,
                'archive_date': False,
            })

            ticket.message_post(
                body=_("🔄 تم استرجاع المذكرة من الأرشيف بواسطة: <b>%s</b>") % self.env.user.name
            )

    @api.depends('ticket_date')
    def _compute_ticket_month(self):
        for record in self:
            if record.ticket_date:
                record.ticket_month = record.ticket_date.strftime('%m')
            else:
                record.ticket_month = False

    @api.depends('ticket_date')
    def _compute_ticket_week(self):
        for record in self:
            if record.ticket_date:
                record.ticket_week = record.ticket_date.strftime('%U')  # الأسبوع في السنة
            else:
                record.ticket_week = False


    @api.depends('ticket_date')
    def _compute_ticket_date_date(self):
        for record in self:
            record.ticket_date_date = record.ticket_date.date() if record.ticket_date else False

    @api.depends('ticket_date')
    def _compute_sequence_year(self):
        for record in self:
            if record.ticket_date:
                record.sequence_year = record.ticket_date.strftime('%Y')
            else:
                record.sequence_year = fields.Date.today().strftime('%Y')


    @api.model
    def _get_next_number(self):
        """Generate next number based on ticket type, section, year, and user (hidden in code only)"""
        today = fields.Date.today()
        year = today.strftime('%Y')

        if not self.ticket_type or not self.ticket_section_id:
            return _('New')

        user_id = self.env.user.id

        # 💡 التسلسل خاص بكل (نوع + قسم + سنة + مستخدم) لكن بدون إظهار اسم المستخدم
        sequence_code = f"docflex.ticket.{self.ticket_type.code}.{self.ticket_section_id.code or 'default'}.{year}.{user_id}"

        # 🔍 البحث عن التسلسل أو إنشائه
        sequence = self.env['ir.sequence'].sudo().search([
            ('code', '=', sequence_code),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if not sequence:
            sequence = self.env['ir.sequence'].sudo().create({
                'name': f'Ticket Sequence - {self.ticket_type.name} - {self.ticket_section_id.name} - {year} - User {user_id}',
                'code': sequence_code,
                'prefix': f"{self.ticket_type.code}/{self.ticket_section_id.code or 'GEN'}/{year}/",
                'padding': 4,
                'number_next': 1,
                'number_increment': 1,
                'company_id': self.company_id.id,
            })

        return sequence.next_by_id()



    @api.model
    def _get_default_ticket_type(self):
        """Get the first available ticket_type with context support"""
        code = self._context.get('code')
        domain = [('code', '=', code)] if code else []
        ticket_type = self.env['ticket.type'].search(domain, order='id asc', limit=1)
        return ticket_type.id if ticket_type else False

    @api.depends('department_id')
    def _compute_domain_user_ids(self):
        for record in self:
            user_ids = []
            if record.department_id:
                # ابحث عن كل الموظفين في القسم المحدد
                employees = self.env['hr.employee'].search([('department_id', '=', record.department_id.id)])
                # اجمع المستخدمين المرتبطين بالموظفين
                user_ids = employees.mapped('user_id.id')
            record.domain_user_ids = [Command.set(user_ids)]

    def _get_partner_email_update(self):
        # منطق التحقق من التحديث
        self.ensure_one()
        return self.partner_email != self.partner_from_id.email if self.partner_from_id else False
    
    @api.depends('partner_email', 'partner_from_id')
    def _compute_is_partner_email_update(self):
        for ticket in self:
            ticket.is_partner_email_update = ticket._get_partner_email_update()
    @api.depends('partner_from_id')
    def _compute_partner_name(self):
        for ticket in self:
            if ticket.partner_from_id:
                ticket.partner_name = ticket.partner_from_id.name

    @api.depends('partner_from_id.phone')
    def _compute_partner_phone(self):
        for ticket in self:
            if ticket.partner_from_id:
                ticket.partner_phone = ticket.partner_from_id.phone
            
    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.partner_from_id.phone and self.partner_phone != self.partner_from_id.phone:
            ticket_phone_formatted = self.partner_phone or False
            partner_phone_formatted = self.partner_from_id.phone or False
            return ticket_phone_formatted != partner_phone_formatted
        return False
    @api.depends('partner_from_id.email')
    def _compute_partner_email(self):
        for ticket in self:
            if ticket.partner_from_id:
                ticket.partner_email = ticket.partner_from_id.email
    def _inverse_partner_email(self):
        for ticket in self:
            if ticket._get_partner_email_update():
                ticket.partner_from_id.email = ticket.partner_email
    def _inverse_partner_phone(self):
        for ticket in self:
            if ticket._get_partner_phone_update() or not ticket.partner_from_id.phone:
                ticket.partner_from_id.phone = ticket.partner_phone

    @api.depends('partner_phone', 'partner_from_id')
    def _compute_is_partner_phone_update(self):
        for ticket in self:
            ticket.is_partner_phone_update = ticket._get_partner_phone_update()

    @api.model
    def _get_default_stage(self):
        stage = self.env['docflex.ticket.stage'].search([], order='sequence asc', limit=1)
        if not stage:
            template = self.env.ref('docflex.email_template_docflex_ticket_default', raise_if_not_found=False)
            stage = self.env['docflex.ticket.stage'].create({
                'name': 'جديد',
                'sequence': 1,
                'is_starting': True,
                'template_id': template.id if template else False,
            })
        return stage.id

    
    @api.model
    def create(self, vals):
        # 1. تعيين معلومات المستخدم
        user = self.env.user
        vals.update({
            'user_id': user.id,
            'user_name': user.name,
        })
        
        #  فقط عيّن القسم إذا لم يكن قد تم تمريره من `default_get`
        if not vals.get('department_id'):
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            if not employee or not employee.department_id:
                raise ValidationError(_("لا يمكنك إنشاء مذكرة لأنك غير مرتبط بقسم. الرجاء التواصل مع مدير النظام."))
            vals['department_id'] = employee.department_id.id
        
        # 3. تعيين المرحلة الافتراضية إذا لم يتم تحديدها
        if 'stage_id' not in vals or not vals.get('stage_id'):
            vals['stage_id'] = self._get_default_stage()
        
        # 4. توليد الرقم التسلسلي
        if vals.get('number', _('New')) == _('New'):
            temp_vals = vals.copy()
            if 'company_id' not in temp_vals:
                temp_vals['company_id'] = self.env.company.id
            temp_ticket = self.new(temp_vals)
            vals['number'] = temp_ticket._get_next_number()
        
        # 5. التأكد من وجود القيم المطلوبة
        required_fields = ['ticket_type', 'ticket_section_id']
        for field in required_fields:
            if field not in vals:
                raise ValidationError(_("حقل %s مطلوب لإنشاء المذكرة") % field)
        
        # 6. إنشاء المذكرة
        ticket = super(DoflexTicket, self).create(vals)
        
        # 7. تسجيل في السجل
        ticket.message_post(body=_("تم إنشاء المذكرة برقم %s") % ticket.number)

            # إرسال البريد الإلكتروني إذا كان هناك قالب مرتبط بالمرحلة
        if ticket.stage_id.template_id:
            ticket.stage_id.template_id.send_mail(ticket.id, force_send=True)
        
        return ticket



    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if employee and employee.department_id:
            res['department_id'] = employee.department_id.id
        return res


    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for ticket in self:
            if ticket.kanban_state == 'normal':
                ticket.kanban_state_label = ticket.legend_normal
            elif ticket.kanban_state == 'blocked':
                ticket.kanban_state_label = ticket.legend_blocked
            else:
                ticket.kanban_state_label = ticket.legend_done

    

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

    # إضافة فهارس لتحسين أداء البحث
    
    def _auto_init(self):
        res = super(DoflexTicket, self)._auto_init()
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_number_idx 
            ON docflex_ticket (number)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_date_idx 
            ON docflex_ticket (ticket_date)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_type_idx 
            ON docflex_ticket (ticket_type)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_section_idx 
            ON docflex_ticket (ticket_section_id)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_status_idx 
            ON docflex_ticket (ticket_status_id)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_priority_idx 
            ON docflex_ticket (ticket_priority_id)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_security_idx 
            ON docflex_ticket (ticket_security_id)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_stage_idx 
            ON docflex_ticket (stage_id)
        """)

        return res

    is_urgent = fields.Boolean(compute='_compute_is_urgent', store=True)

    @api.depends('ticket_priority_id')
    def _compute_is_urgent(self):
        for rec in self:
            rec.is_urgent = rec.ticket_priority_id.name == 'عاجل'