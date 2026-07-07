{
    'name': 'Portfolio Modules',
    'version': '1.0',
    'author': 'Amul Babariya',
    'category': 'Website',
    'summary': 'Showcase your custom Odoo modules on your portfolio website.',
    'depends': ['website', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/portfolio_module_views.xml',
        'views/portfolio_module_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portfolio_module/static/src/css/portfolio_module.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
