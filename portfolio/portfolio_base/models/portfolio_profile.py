from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PortfolioProfile(models.Model):
    _name = 'portfolio.profile'
    _description = 'Portfolio Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, tracking=True)
    date_of_birth = fields.Date(string='Date of Birth')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=?', country_id)]")
    city = fields.Char(string='City')
    
    linkedin_url = fields.Char(string='LinkedIn URL')
    github_url = fields.Char(string='GitHub URL')
    
    resume = fields.Binary(string='Resume')
    resume_name = fields.Char(string='Resume File Name')
    
    about_me = fields.Html(string='About Me')
    short_intro = fields.Text(string='Short Introduction')
    
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    
    total_experience = fields.Char(string='Total Experience', compute='_compute_total_experience')
    
    education_ids = fields.One2many('portfolio.education', 'profile_id', string='Education')
    experience_ids = fields.One2many('portfolio.experience', 'profile_id', string='Experience')
    skill_ids = fields.One2many('portfolio.skill', 'profile_id', string='Skills')
    language_ids = fields.One2many('portfolio.language', 'profile_id', string='Languages')

    @api.depends('experience_ids.experience_duration')
    def _compute_total_experience(self):
        for record in self:
            total_months = 0
            for exp in record.experience_ids:
                if exp.start_date:
                    end = exp.end_date or fields.Date.today()
                    if end > exp.start_date:
                        delta = end - exp.start_date
                        # Approximate months
                        total_months += int(delta.days / 30.416)
            
            years = total_months // 12
            months = total_months % 12
            
            if years > 0 and months > 0:
                record.total_experience = f"{years} Years {months} Months"
            elif years > 0:
                record.total_experience = f"{years} Years"
            elif months > 0:
                record.total_experience = f"{months} Months"
            else:
                record.total_experience = "0 Months"

    @api.model_create_multi
    def create(self, vals_list):
        if self.search_count([]) > 0:
            raise ValidationError("You can only create one Portfolio Profile.")
        return super().create(vals_list)

    def unlink(self):
        raise ValidationError("You cannot delete the Portfolio Profile.")
