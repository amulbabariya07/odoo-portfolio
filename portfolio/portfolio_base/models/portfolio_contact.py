from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PortfolioContact(models.Model):
    _name = 'portfolio.contact'
    _description = 'Portfolio Contact Inquiry'
    _order = 'create_date desc'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    description = fields.Text(string='Message/Description', required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status', default='new', required=True, group_expand='_expand_states')
    
    color = fields.Integer(string='Color Index')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        
        mail_server_portfolio = self.env['ir.mail_server'].sudo().search([('smtp_user', '=', 'portfolio.amul@gmail.com')], limit=1)
        mail_server_amul = self.env['ir.mail_server'].sudo().search([('smtp_user', '=', 'amulbabariya07@gmail.com')], limit=1)
        
        db_name = self.env.cr.dbname
        mail_ids_to_send = []

        for record in records:
            # Send Notification to Admin
            if mail_server_portfolio:
                admin_template = self.env.ref('portfolio_base.email_template_portfolio_contact_admin', raise_if_not_found=False)
                if admin_template:
                    email_values = {
                        'mail_server_id': mail_server_portfolio.id,
                        'email_to': 'amulbabariya07@gmail.com'
                    }
                    
                    # Include multiple attachments if the user uploaded them
                    if record.attachment_ids:
                        email_values['attachment_ids'] = record.attachment_ids.ids
                        
                    mail_id = admin_template.sudo().send_mail(
                        record.id,
                        force_send=False,
                        email_values=email_values
                    )
                    mail_ids_to_send.append(mail_id)

            # Send Auto-reply to Client
            if mail_server_amul and record.email:
                client_template = self.env.ref('portfolio_base.email_template_portfolio_contact_client', raise_if_not_found=False)
                if client_template:
                    mail_id = client_template.sudo().send_mail(
                        record.id,
                        force_send=False,
                        email_values={'mail_server_id': mail_server_amul.id}
                    )
                    mail_ids_to_send.append(mail_id)
                    
        if mail_ids_to_send:
            import threading
            from odoo import api, SUPERUSER_ID
            from odoo.modules.registry import Registry
            
            def send_async_emails(db_name, mail_ids):
                db_registry = Registry(db_name)
                with db_registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    mails = env['mail.mail'].browse(mail_ids)
                    mails.send()
                    
            thread = threading.Thread(target=send_async_emails, args=(db_name, mail_ids_to_send))
            thread.start()

        return records

    @api.model
    def _expand_states(self, values, domain):
        return ['new', 'in_progress', 'done']

    @api.constrains('email', 'phone')
    def _check_contact_info(self):
        for record in self:
            if not record.email and not record.phone:
                raise ValidationError("Please provide at least an Email address or a Phone number so we can reach you.")

    def action_open_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'portfolio.contact',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

