from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    name = fields.Char(
        required=False,
        track_visibility='always',
    )
