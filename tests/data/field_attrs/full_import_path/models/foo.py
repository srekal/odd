import odoo


class Foo(odoo.models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = odoo.fields.Many2one(
        comodel_name='bar',
        selection=True,
    )
