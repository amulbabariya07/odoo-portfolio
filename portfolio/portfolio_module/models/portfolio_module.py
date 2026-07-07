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

    @api.constrains('is_featured')
    def _check_featured_limit(self):
        for record in self:
            if record.is_featured:
                featured_count = self.env['portfolio.module'].search_count([('is_featured', '=', True)])
                if featured_count > 6:
                    raise ValidationError("You can only feature a maximum of 6 modules on the home page.")
