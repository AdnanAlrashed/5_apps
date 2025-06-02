from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import logging

_logger = logging.getLogger(__name__)
class LibraryBook(models.Model):
    _name = 'library.book'
    _description = _('الكتاب')
    _sql_constraints = [
        ('check_publication_date', 'CHECK(publication_date <= CURRENT_DATE)', 
         'The publication date cannot be in the future!')
    ]


    name = fields.Char(string=_("العنوان"), required=True)
    isbn = fields.Char(_("رقم الكتاب الدولي"), required=True)
    is_available = fields.Boolean(string="متاح", default=True)
    copies_sold = fields.Integer(_("عدد النسخ المباعة"), description="عدد النسخ", default=0)
    author_id = fields.Many2one('library.author', string="المالك")
    publisher_id = fields.Many2one(
        "res.partner",
        string="الناشر"
    )
    publication_date = fields.Date(string="تاريخ النشر", default=date.today())
    # price = fields.Float(string="السعر", digits=(6, 2))
    price = fields.Float(
        string="السعر",
        digits=("library_book_price", 2),  # التحكم في الدقة عبر إعدادات النظام
        help="Book price with configurable precision"
    )
    monetary_value = fields.Monetary(
        string="القيمه",
        currency_field="currency_id"
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="العملة",
        default=lambda self: self.env.company.currency_id
    )
    co_authors = fields.Many2many(
        "library.author",
        string="مؤلف مشارك"
    )

    user_id = fields.Many2one('res.users', string="تم إنشاؤه بواسطة", default=lambda self: self.env.user)
    discount_price = fields.Float(string="السعر بعد الخصم", compute="_compute_discount_price", store=True)
    
    copy_ids = fields.One2many('library.book.copy', 'book_id', string="النسخ")

    @api.depends('price')
    def _compute_discount_price(self):
        """حساب الخصم بناءً على إعدادات النظام"""
        enable_auto_discount = self.env['ir.config_parameter'].sudo().get_param('library.enable_auto_discount', 'False') == 'True'
        discount_rate = float(self.env['ir.config_parameter'].sudo().get_param('library.default_discount_rate', '0.0'))

        for record in self:
            if enable_auto_discount:
                record.discount_price = record.price * (1 - discount_rate / 100)
            else:
                record.discount_price = record.price


    @api.model
    def _get_domain_books(self):
        """إرجاع النطاق بناءً على دور المستخدم."""
        if self.env.user.has_group('base.group_system'):  # إذا كان المستخدم Admin
            return []  # عرض جميع الكتب
        return [('user_id', '=', self.env.user.id)]  # عرض الكتب التي أنشأها المستخدم العادي فقط

    @api.model
    def get_books(self):
        """إحضار الكتب بناءً على دور المستخدم."""
        domain = self._get_domain_books()
        return self.search(domain)

    @api.model
    def post_install_hook(self):
        # تنفيذ إجراء معين عند تثبيت الوحدة
        _logger.info("📚 Library module installed - Post-install function executed!")

    @api.constrains('publication_date')
    def _check_publication_date(self):
        for book in self:
            if book.publication_date and book.publication_date > date.today():
                raise ValidationError("The publication date cannot be in the future!")

    @api.constrains("co_authors", "author_id")
    def _check_co_authors(self):
        """تأكد من أن المؤلف الرئيسي ليس ضمن المؤلفين المشاركين."""
        for book in self:
            if book.author_id and book.author_id in book.co_authors:
                raise ValidationError("The main author cannot be a co-author.")
            
    @api.onchange("author_id")
    def _onchange_author_id(self):
        """ملء `publisher_id` تلقائيًا إذا كان للمؤلف ناشر افتراضي."""
        if self.author_id and self.author_id.default_publisher_id:
            self.publisher_id = self.author_id.default_publisher_id

    @api.constrains("monetary_value")
    def _check_monetary_value(self):
        """Constraint on negative rent amount"""
        if self.monetary_value == 0:
            raise ValidationError(_("Rent Amount Per Month should not be a negative value!"))

    def action_view_copies(self):
        """ زر لعرض جميع النسخ الخاصة بالكتاب """
        return {
            'type': 'ir.actions.act_window',
            'name': _('نسخ الكتاب'),
            'res_model': 'library.book.copy',
            'view_mode': 'tree,form',
            'domain': [('book_id', '=', self.id)],
            'context': {'default_book_id': self.id},
        }


    def custom_function(self):
        """تنفيذ الدالة بناءً على قيمة `custom_flag` في `context`."""
        custom_flag = self.env.context.get('custom_flag')

        if custom_flag == 'fast_mode':
            return "تم التنفيذ بوضع السرعة"
        elif custom_flag == 'safe_mode':
            return "تم التنفيذ بوضع الأمان"
        else:
            return "تم التنفيذ بالوضع العادي"
        
        books = self.with_context(custom_flag='fast_mode').custom_function()
        print(books)  # النتيجة: "تم التنفيذ بوضع السرعة"



    @api.model
    def create_book(self, name, isbn, author_id, publisher_id, price):
        """إنشاء سجل جديد للكتاب"""
        new_book = self.create({
            'name': name,
            'isbn': isbn,
            'author_id': author_id,
            'publisher_id': publisher_id,
            'price': price,
            'is_available': True
        })
        return new_book

    def update_book_price(self, new_price):
        """تحديث سعر الكتاب الحالي"""
        self.ensure_one()  # تأكد أن العملية تتم على سجل واحد فقط
        self.write({'price': new_price})
        return True

    def delete_book(self):
        """حذف الكتاب"""
        self.ensure_one()
        self.unlink()
        return True

class LibraryBookCopy(models.Model):
    _name = 'library.book.copy'
    _inherits = {'library.book': 'book_id'}
    _description = _('نسخة من الكتاب')

    book_id = fields.Many2one('library.book', required=True, ondelete='cascade')
    status = fields.Selection([
        ('available', 'متاح'),
        ('borrowed', 'مستعار'),
        ('lost', 'مفقود'),
    ], string="الحالة", default="available")