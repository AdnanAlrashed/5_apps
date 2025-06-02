from odoo import fields, models, api

class LibraryPublisher(models.Model):
    _name = 'library.publisher'
    _description = 'الناشر'

    name = fields.Char(string='اسم الناشر', description='اسم الناشر')
    book_ids = fields.One2many('library.book', 'publisher_id', string='الكتب')
    total_revenue = fields.Float(compute="_cumpute_total_revenue", string="اجمالي الايرادات")

    def _cumpute_total_revenue(self):
        pass