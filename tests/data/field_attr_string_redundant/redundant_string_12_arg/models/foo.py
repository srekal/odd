from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    some_value = fields.Char('Some Value')
