# -*- coding: utf-8 -*-
{
    'name': "الاتصالات الادراية",
    'summary': "Short (1 phrase/line) summary of the module's purpose",
    'description': """
            Long description of module's purpose
                """,
    'author': "AIZERP Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'module_type':'official',
    'version': '17.0.1.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','hr','mail',
                'website',
                'helpdesk',
                'documents',
                'utm',
                'rating',
                'web_tour',
                'web_cohort',
                'resource',
                'portal',
                'digest',
                ],

    # always loaded
    'data': [
        'data/data.xml',
        'data/email_templates.xml',
        'security/docflex_security.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
        'views/docflex_ticket_views.xml',
        'views/ticket_classification_views.xml',
        'views/ticket_sections_views.xml',
        'views/ticket_status_views.xml',
        'views/ticket_priority_views.xml',
        'views/ticket_type_views.xml',
        'views/ticket_summary_views.xml',
        'views/ticket_tag_views.xml',
        'views/ticket_security_views.xml',
        'views/docflex_ticket_stage_views.xml',
        'views/res_partner_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
           
        ],
        'web.qunit_suite_tests': [
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',

    'installable':True,
    'application':True,
    'license':'LGPL-3',
}

