{
    'name': 'Pharmacy',
    'version': '1.0',
    'depends': ['base', 'product', 'sale', 'stock'],
    'author': 'Adnan Alrashed',
    'category': 'Hospital/Midcal',
    'description': 'Pharmacy Prescription Midicen',
    'data': [
        'security/ir.model.access.csv',
        'data/prescription_sequence.xml',
        'reports/prescription_report.xml',
        'views/prescription_views.xml',
        'views/menu_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,

}