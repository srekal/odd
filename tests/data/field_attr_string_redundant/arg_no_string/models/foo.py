from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    partner_id = fields.Many2one('res.partner')
