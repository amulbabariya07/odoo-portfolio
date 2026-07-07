from odoo import models, fields

class PortfolioModuleTag(models.Model):
    _name = 'portfolio.module.tag'
    _description = 'Portfolio Module Tag'

    name = fields.Char(string='Name', required=True)
