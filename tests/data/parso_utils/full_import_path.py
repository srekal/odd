import odoo


class Foo(odoo.models.Model):
    _name = 'foo'

    bar = odoo.fields.Char()
