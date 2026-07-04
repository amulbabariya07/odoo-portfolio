from odoo import models, fields

class PortfolioEducation(models.Model):
    _name = 'portfolio.education'
    _description = 'Portfolio Education'
    _order = 'sequence, start_year desc, id'

    profile_id = fields.Many2one('portfolio.profile', string='Profile', required=True, ondelete='cascade')
    school_name = fields.Char(string='School / University Name', required=True)
    degree = fields.Char(string='Degree')
    
    start_year = fields.Char(string='Start Year', size=4)
    end_year = fields.Char(string='End Year', size=4)
    is_continue = fields.Boolean(string='Continue')
    
    score = fields.Char(string='CGPA / Percentage')
    description = fields.Text(string='Description')
    sequence = fields.Integer(default=10)
