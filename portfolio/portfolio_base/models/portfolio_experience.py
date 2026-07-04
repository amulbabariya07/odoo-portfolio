from odoo import models, fields, api

class PortfolioExperience(models.Model):
    _name = 'portfolio.experience'
    _description = 'Portfolio Experience'
    _order = 'start_date desc, id'

    profile_id = fields.Many2one('portfolio.profile', string='Profile', required=True, ondelete='cascade')
    company_name = fields.Char(string='Company Name', required=True)
    role = fields.Char(string='Role / Position')
    employment_type = fields.Selection([
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship')
    ], string='Employment Type')
    location = fields.Char(string='Location')
    
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date')
    is_currently_working = fields.Boolean(string='Currently Working')
    
    experience_duration = fields.Char(string='Experience', compute='_compute_experience_duration')
    
    description = fields.Text(string='Description')
    sequence = fields.Integer(default=10)

    @api.depends('start_date', 'end_date', 'is_currently_working')
    def _compute_experience_duration(self):
        for record in self:
            if record.start_date:
                end = fields.Date.today() if record.is_currently_working else (record.end_date or fields.Date.today())
                if end > record.start_date:
                    delta = end - record.start_date
                    total_months = int(delta.days / 30.416)
                    years = total_months // 12
                    months = total_months % 12
                    
                    if years > 0 and months > 0:
                        record.experience_duration = f"{years} Years {months} Months"
                    elif years > 0:
                        record.experience_duration = f"{years} Years"
                    elif months > 0:
                        record.experience_duration = f"{months} Months"
                    else:
                        record.experience_duration = "0 Months"
                else:
                    record.experience_duration = "0 Months"
            else:
                record.experience_duration = False
