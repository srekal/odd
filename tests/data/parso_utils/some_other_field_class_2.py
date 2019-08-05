import django

from odoo import models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = django.fields.Float()
