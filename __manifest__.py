{
    'name': 'Smart ERP Automation',
    'version': '1.0',
    'depends': ['sale', 'stock', 'purchase', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/automation_rule_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
}