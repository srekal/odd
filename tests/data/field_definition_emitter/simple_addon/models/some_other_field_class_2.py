import django

from odoo import models


class Foo(models.Model):
    _name = 'foo'

    bar = django.fields.Float()
