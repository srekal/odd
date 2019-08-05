import it

from odoo import models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = it.we.all.Float()
