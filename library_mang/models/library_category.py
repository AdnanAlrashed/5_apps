from odoo import models, fields, api

class LibraryCategory(models.Model):
    _name = "library.category"
    _description = "Book Category"

    name = fields.Char(string="Category Name", required=True)
    parent_id = fields.Many2one(
        "library.category",
        string="Parent Category",
        index=True,
        ondelete="cascade"
    )
    child_ids = fields.One2many(
        "library.category",
        "parent_id",
        string="Subcategories"
    )
