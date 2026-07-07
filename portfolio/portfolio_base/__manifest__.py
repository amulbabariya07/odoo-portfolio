{
    'name': 'Portfolio Base',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Personal Portfolio Theme for Home Page',
    'description': """
        Provides a responsive white-background portfolio for the main website route (/).
        Features custom CSS separated from HTML.
    """,
    'depends': ['website', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/website_data.xml',
        'data/mail_template_data.xml',
        'views/portfolio_profile_views.xml',
        'views/portfolio_education_views.xml',
        'views/portfolio_experience_views.xml',
        'views/portfolio_skill_views.xml',
        'views/portfolio_language_views.xml',
        'views/portfolio_contact_views.xml',
        'views/portfolio_templates.xml',
        'views/portfolio_contact_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portfolio_base/static/src/css/portfolio.css',
            'portfolio_base/static/src/css/portfolio_contact.css',
            'portfolio_base/static/src/js/portfolio.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
