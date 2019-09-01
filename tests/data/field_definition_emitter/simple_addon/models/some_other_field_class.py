import it

from odoo import models


class Foo(models.Model):
    _name = 'foo'

    bar = it.we.all.Float()
