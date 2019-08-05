from openerp import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    name = fields.Char(
        string='Name',
    )
