import django


class Foo(django.db.models.Model):
    _name = 'foo'

    bar = django.fields.Many2one(
        String='Bar',
    )
