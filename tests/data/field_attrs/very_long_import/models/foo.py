import baz


class Foo(baz.odoo.models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = baz.odoo.fields.Char(
        size=1,
    )
