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
    attachment = fields.Binary(string='Attachment')
    attachment_name = fields.Char(string='Attachment Name')
    
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status', default='new', required=True, group_expand='_expand_states')
    
    color = fields.Integer(string='Color Index')

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

