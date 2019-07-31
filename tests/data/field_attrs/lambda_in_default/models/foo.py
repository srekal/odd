from odoo import fields, models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = fields.Many2one(
        comodel_name='bar',
        string='Bar',
        default=lambda self: self.env.ref(
            'lambda_in_default.baz',
            raise_if_not_found=False,
        ),
    )
