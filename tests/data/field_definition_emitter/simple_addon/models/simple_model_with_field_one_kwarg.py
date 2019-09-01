from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'

    bar = fields.Char(
        string="Bar",
    )
