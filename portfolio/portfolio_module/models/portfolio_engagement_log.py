from odoo import models, fields

class PortfolioEngagementLog(models.Model):
    _name = 'portfolio.engagement.log'
    _description = 'Engagement Email Log'
    _order = 'create_date desc'

    module_id = fields.Many2one('portfolio.module', string='Module', required=False, ondelete='cascade')
    email_temp_id = fields.Many2one('email.temp', string='Email Template', required=False, ondelete='cascade')
    client_id = fields.Many2one('my.clients', string='Client', required=True, ondelete='cascade')
