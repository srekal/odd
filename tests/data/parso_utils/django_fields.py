from django.db import models


class Foo(models.Model):
    _name = 'foo'
    _description = 'Foo'

    bar = models.fields.Many2one(
        String='Bar',
    )
