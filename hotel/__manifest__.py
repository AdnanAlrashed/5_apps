# -*- coding: utf-8 -*-
{
    'name': "hotel",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Adnan",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'adnan/hotel',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','product'],

    # always loaded
    'data': [
        "security/hostel_security.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        'security/security_rules.xml',
        "views/hostel.xml",
        "views/hostel_room.xml",
        "views/hostel_room_category_view.xml",
        "views/res_config_settings_views.xml",
        "wizard/assign_room_student.xml",
        "wizard/hostel_room_wizard_view.xml",
        "data/data.xml",
        "data/demo.xml",
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

