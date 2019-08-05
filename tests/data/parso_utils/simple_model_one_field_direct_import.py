from odoo import models
from odoo.fields import Char


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = Char()
