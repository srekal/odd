from odoo import fields, models


class Foo(models.Model):
    _description = 'Foo'

    bar = fields.Char(
        size=2,
    )
