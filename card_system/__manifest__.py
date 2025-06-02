{
    "name": "ID Card System",
    "version": "1.0",
    "depends": ["base", 'mail'],
    "author": "Adnan Alrashed",
    "category": "Gov/Tools",
    "summary": "System for managing national ID cards",
    "data": [
        "security/card_system_security.xml",
        "security/ir.model.access.csv",
        "views/citizen_views.xml",
        "views/card_views.xml",
        "views/request_views.xml",
        "views/biometric_views.xml",
        "views/branch_views.xml",
        "views/menu.xml",
        # "data/citizen_dome.xml",
        "data/sequence.xml",
    ],
    "installable": True,
    "application": True
}
