from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MyClients(models.Model):
    _name = 'my.clients'
    _description = 'My Clients'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    active = fields.Boolean(string="Active", default=True)
    
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

    def action_send_welcome_email(self):
        template = self.env.ref('portfolio_module.email_template_welcome_client')

        # Get up to 6 featured modules
        featured_modules = self.env['portfolio.module'].search([('is_featured', '=', True)], limit=6)

        # Explicitly find outgoing mail server
        mail_server = self.env['ir.mail_server'].sudo().search([('smtp_user', '=', 'amulbabariya07@gmail.com')], limit=1)

        count = 0
        for client in self:
            if not client.active or not client.email:
                continue

            ctx = dict(self.env.context)
            ctx['featured_modules'] = featured_modules

            email_values = {
                'email_to': client.email,
            }
            if mail_server:
                email_values['mail_server_id'] = mail_server.id

            template.with_context(ctx).send_mail(client.id, force_send=True, email_values=email_values)
            count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Welcome Emails Sent',
                'message': f'Successfully sent {count} welcome emails!',
                'type': 'success',
                'sticky': False,
            }
        }
