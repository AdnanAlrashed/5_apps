from odoo import fields, models

class LibraryBookReport(models.Model):
    _name = 'library.book.report'
    _description = 'تقرير الكتب'

    publisher_id = fields.Many2one('library.publisher', string='الناشر')
    book_count = fields.Integer(string='عددالكتب')
    total_revenue = fields.Float(string='اجمالي الايرادات')

    def init(self):
        pass