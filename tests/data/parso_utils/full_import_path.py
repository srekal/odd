import odoo


class Foo(odoo.models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = odoo.fields.Char()
