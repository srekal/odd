from openerp import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    value = fields.Monetary(
        string='Value',
    )
