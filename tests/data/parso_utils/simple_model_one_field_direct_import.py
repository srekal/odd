from odoo import models
from odoo.fields import Char


class Foo(models.Model):
    _name = 'foo'

    bar = Char()
