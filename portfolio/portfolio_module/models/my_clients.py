from odoo import models, fields

class MyClients(models.Model):
    _name = 'my.clients'
    _description = 'My Clients'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    
    engagement_log_ids = fields.One2many('portfolio.engagement.log', 'client_id', string='Engagement Logs')
    engagement_count = fields.Integer(compute='_compute_engagement_count', string='Emails Received')

    def _compute_engagement_count(self):
        for rec in self:
            rec.engagement_count = len(rec.engagement_log_ids)

    def action_open_engagement_logs(self):
        self.ensure_one()
        return {
            'name': 'Engagement Emails',
            'type': 'ir.actions.act_window',
            'res_model': 'portfolio.engagement.log',
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id},
        }
