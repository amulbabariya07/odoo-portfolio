from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MyClients(models.Model):
    _name = 'my.clients'
    _description = 'My Clients'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    
    engagement_log_ids = fields.One2many('portfolio.engagement.log', 'client_id', string='Engagement Logs')
    engagement_count = fields.Integer(compute='_compute_engagement_count', string='Emails Received')

    @api.constrains('name', 'email')
    def _check_unique_client(self):
        for record in self:
            if record.name and record.email:
                existing_client = self.search([
                    ('name', '=', record.name),
                    ('email', '=', record.email),
                    ('id', '!=', record.id)
                ], limit=1)

                if existing_client:
                    raise ValidationError(f"This record is already created with ID {existing_client.id} ({existing_client.name}).")

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
