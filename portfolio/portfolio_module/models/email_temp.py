from odoo import models, fields, api
from odoo.exceptions import UserError

class EmailTemp(models.Model):
    _name = 'email.temp'
    _description = 'Custom Email Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Name', required=True, tracking=True)
    subject = fields.Char(string='Subject', required=True, tracking=True)
    body_arch = fields.Html(string='Body', translate=False, sanitize=False)
    body_html = fields.Html(string='Body (HTML)', sanitize=False)
    editor_mode = fields.Selection([
        ('drag_drop', 'Drag and Drop Email'),
        ('code', 'Code Email')
    ], string="Design Mode", default='drag_drop', required=True, tracking=True)
    body_raw_html = fields.Html(string='Custom HTML Code', sanitize=False)
    
    mailing_model_id = fields.Many2one(
        'ir.model', string='Recipient Model',
        default=lambda self: self.env['ir.model'].search([('model', '=', 'my.clients')], limit=1)
    )
    
    test_client_ids = fields.Many2many('my.clients', string='Select Clients (Personal Send)')
    
    @api.onchange('editor_mode')
    def _onchange_editor_mode(self):
        # When switching to Code Editor, automatically load the Drag & Drop HTML
        # so the user can continue editing the code of their drag & drop design!
        for rec in self:
            if rec.editor_mode == 'code':
                if not rec.body_raw_html or rec.body_raw_html in ('<p><br></p>', '<p></p>'):
                    rec.body_raw_html = rec.body_html
    
    engagement_log_ids = fields.One2many('portfolio.engagement.log', 'email_temp_id', string='Engagement Logs')
    engagement_count = fields.Integer(compute='_compute_engagement_count', string='Emails Sent')

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
            'domain': [('email_temp_id', '=', self.id)],
            'context': {'default_email_temp_id': self.id},
        }

    def _create_and_send_mail(self, client, force_send=False):
        """Helper to create standard mail.mail record."""
        mail_server = self.env['ir.mail_server'].sudo().search([('smtp_user', '=', 'amulbabariya07@gmail.com')], limit=1)
        
        # Decide which body to use based on the mode
        if self.editor_mode == 'code':
            final_body = self.body_raw_html
        else:
            final_body = self.body_html
            
        # Convert relative image URLs (like /web/image/...) to absolute URLs so they load in Gmail
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if final_body and base_url:
            final_body = final_body.replace('src="/', f'src="{base_url}/')
            
        mail_values = {
            'subject': self.subject,
            'body_html': final_body,
            'email_to': client.email,
            'email_from': 'Amul Babariya <amulbabariya07@gmail.com>',
            'auto_delete': False,  # Keep log in Odoo
        }
        if mail_server:
            mail_values['mail_server_id'] = mail_server.id
            
        mail = self.env['mail.mail'].sudo().create(mail_values)
        if force_send:
            mail.send()
        
        # Log the engagement
        self.env['portfolio.engagement.log'].create({
            'email_temp_id': self.id,
            'client_id': client.id,
        })
        return mail

    def action_send_personally(self):
        self.ensure_one()
        if not self.test_client_ids:
            raise UserError("Please select at least one client.")
            
        count = 0
        for client in self.test_client_ids:
            if not client.email:
                continue
            self._create_and_send_mail(client, force_send=True)
            count += 1
            
        if count == 0:
            raise UserError("None of the selected clients have an email address.")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Emails Sent',
                'message': f'Successfully sent emails to {count} clients!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_send_all_clients(self):
        self.ensure_one()
        
        # Find clients that haven't received this template yet
        sent_logs = self.env['portfolio.engagement.log'].search([('email_temp_id', '=', self.id)])
        sent_client_ids = sent_logs.mapped('client_id.id')
        
        domain = [('email', '!=', False), ('active', '=', True)]
        if sent_client_ids:
            domain.append(('id', 'not in', sent_client_ids))
            
        clients = self.env['my.clients'].search(domain)
        
        if not clients:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Emails Sent',
                    'message': 'All active clients have already received this email, or no active clients have an email address.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
            
        count = 0
        for client in clients:
            # We don't force send here. 
            # Odoo cron "Mail: Email Queue Manager" will pick these up and process them slowly in batches.
            self._create_and_send_mail(client, force_send=False)
            count += 1
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Emails Queued',
                'message': f'{count} emails have been successfully queued. The server will send them slowly in the background.',
                'type': 'success',
                'sticky': False,
            }
        }
