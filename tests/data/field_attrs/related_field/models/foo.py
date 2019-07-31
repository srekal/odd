from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    other = fields.Many2one(
        comodel_name='baz',
    )
    bar = fields.Char(
        related='other.bar',
    )
