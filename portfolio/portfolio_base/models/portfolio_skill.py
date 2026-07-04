from odoo import models, fields

class PortfolioSkill(models.Model):
    _name = 'portfolio.skill'
    _description = 'Portfolio Skill'
    _order = 'sequence, id'

    profile_id = fields.Many2one('portfolio.profile', string='Profile', required=True, ondelete='cascade')
    name = fields.Char(string='Skill Name', required=True)
    icon = fields.Image(string='Icon Image', max_width=256, max_height=256)
    description = fields.Text(string='Description')
    sequence = fields.Integer(default=10)
