from odoo import models, fields

class PortfolioLanguage(models.Model):
    _name = 'portfolio.language'
    _description = 'Portfolio Language'

    profile_id = fields.Many2one('portfolio.profile', string='Profile', required=True, ondelete='cascade')
    name = fields.Char(string='Language', required=True)
    level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('professional', 'Professional'),
        ('native', 'Native')
    ], string='Level', required=True, default='intermediate')
    description = fields.Text(string='Description')
