# -*- coding: utf-8 -*-
{
    'name': "Library Manag",

    'summary': "Manage All Books in Library",

    'description': """
Add Books and Author for books
    """,

    'author': "Adnan",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'adnan/library',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/library_book_views.xml",
        "views/library_book_views.xml",
        "views/res_config_settings.xml",
        "data/library_book_data.xml",
        # "data/demo.xml",
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

