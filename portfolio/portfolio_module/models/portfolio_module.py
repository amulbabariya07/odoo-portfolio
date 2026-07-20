from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PortfolioModule(models.Model):
    _name = 'portfolio.module'
    _description = 'Portfolio Module'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, tracking=True)
    short_description = fields.Char(string='Short Description', tracking=True)
    long_description = fields.Html(string='Long Description')
    image = fields.Image(string='Image')
    tag_ids = fields.Many2many('portfolio.module.tag', string='Tags', tracking=True)
    sequence = fields.Integer(string='Sequence', default=10, tracking=True)
    
    version = fields.Selection([
        ('11.0', '11.0'),
        ('12.0', '12.0'),
        ('13.0', '13.0'),
        ('14.0', '14.0'),
        ('15.0', '15.0'),
        ('16.0', '16.0'),
        ('17.0', '17.0'),
        ('18.0', '18.0'),
        ('19.0', '19.0'),
    ], string='Version', tracking=True)
    
    module_ids = fields.Many2many('ir.module.module', string='Modules', tracking=True)
    is_featured = fields.Boolean(string='Show on Home Page', default=False, tracking=True)
    
    engagement_log_ids = fields.One2many('portfolio.engagement.log', 'module_id', string='Engagement Logs')
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
            'domain': [('module_id', '=', self.id)],
            'context': {'default_module_id': self.id},
        }

    def action_send_engagement_email(self):
        self.ensure_one()
        
        # Find clients that haven't received an email for this module yet
        sent_logs = self.env['portfolio.engagement.log'].search([('module_id', '=', self.id)])
        sent_client_ids = sent_logs.mapped('client_id.id')
        
        domain = [('email', '!=', False)]
        if sent_client_ids:
            domain.append(('id', 'not in', sent_client_ids))
            
        clients = self.env['my.clients'].search(domain)
        
        if not clients:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Emails Sent',
                    'message': 'All valid clients have already received an email for this module, or no clients have an email address.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        template = self.env.ref('portfolio_module.email_template_engagement_custom')
        count = 0
        
        # Explicitly find outgoing mail server
        mail_server = self.env['ir.mail_server'].sudo().search([('smtp_user', '=', 'amulbabariya07@gmail.com')], limit=1)
        
        for client in clients:
            # Create Log
            log = self.env['portfolio.engagement.log'].create({
                'module_id': self.id,
                'client_id': client.id,
            })
            
            # Context for template
            ctx = dict(self.env.context)
            ctx['contact_name'] = client.name
            
            # Send Email
            email_values = {
                'email_to': client.email,
            }
            if mail_server:
                email_values['mail_server_id'] = mail_server.id
                
            template.with_context(ctx).send_mail(log.id, force_send=True, email_values=email_values)
            count += 1
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Emails Sent',
                'message': f'Successfully sent {count} engagement emails!',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.constrains('is_featured')
    def _check_featured_limit(self):
        for record in self:
            if record.is_featured:
                featured_count = self.env['portfolio.module'].search_count([('is_featured', '=', True)])
                if featured_count > 6:
                    raise ValidationError("You can only feature a maximum of 6 modules on the home page.")
