from odoo import models
from odoo.fields import Many2one


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = Many2one(
        comodel_name='bar',
        translate=True,
    )
