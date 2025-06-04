# -*- coding: utf-8 -*-
# from odoo import http


# class Docflex(http.Controller):
#     @http.route('/docflex/docflex', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/docflex/docflex/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('docflex.listing', {
#             'root': '/docflex/docflex',
#             'objects': http.request.env['docflex.docflex'].search([]),
#         })

#     @http.route('/docflex/docflex/objects/<model("docflex.docflex"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('docflex.object', {
#             'object': obj
#         })

