from odoo import fields, models, api

class Author(models.Model):
    _name = 'library.author'
    inherit = "res.partner"
    _description = 'المؤلف'

    name = fields.Char(string="Author Name", required=True)
    biography = fields.Text(string='السيره الذاتيه')
    total_books_published = fields.Integer(string='اجمالي الكتب المنشوره', compute='_compute_total_books_published')
    book_ids = fields.One2many('library.book', 'author_id', string='الكتب')
    default_publisher_id = fields.Many2one('library.publsher', string='الناشر الافتراضي',
                                           help="The default publisher for books by this author")
    is_author = fields.Boolean(string="Is Author", default=False)
    reference_id = fields.Reference(
    selection=[
        ("res.partner", "Partner"),
        ("library.publisher", "Publisher")
    ],
    string="Reference Entity"
)

    @api.depends('book_ids')  # تحديد أن الحساب يعتمد على حقل book_ids
    def _compute_total_books_published(self):
        for author in self:
            author.total_books_published = len(author.book_ids) 