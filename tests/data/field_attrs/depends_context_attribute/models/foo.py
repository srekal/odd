from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    other_id = fields.Many2one(
        comodel_name='baz',
    )
    bar = fields.Text(
        related='other_id.some_field',
        readonly=False,
        depends_context=('some_key',),
    )
